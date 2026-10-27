"""Isolated temporary files and mocked Connector; never touches a real library."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pypdf import PdfWriter

spec = importlib.util.spec_from_file_location("workflow", Path(__file__).parents[1] / "scripts/workflow.py")
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.config = self.base / "config.json"
        self.paper = self.base / "paper.json"
        self.pdf = self.base / "input.pdf"
        self.work = self.base / "task"
        wf.write_json(self.config, {"paper_root": "papers", "collection_name": "气候变化下的土壤碳循环"})
        self.data = {"number": 7, "date": "2026-10-27", "title": "Synthetic Soil Study",
                     "title_zh": "虚构土壤研究", "journal": "Test Journal", "year": 2024,
                     "doi": "10.0000/test", "url": "https://example.org/paper",
                     "pdf_source": "https://example.org/paper.pdf", "authors": [],
                     "sections": [{"heading": "测试结论", "text": "仅用于隔离验证，不是真实研究。"}]}
        wf.write_json(self.paper, self.data)
        writer = PdfWriter()
        writer.add_blank_page(width=595, height=842)
        with self.pdf.open("wb") as stream:
            writer.write(stream)

    def prepare(self):
        return wf.prepare(self.config, self.paper, self.pdf, self.work)

    def selected(self):
        return {"targets": [{"name": "气候变化下的土壤碳循环", "id": "C99", "filesEditable": True}]}

    def test_bundle_number_and_note_name(self):
        state = self.prepare()
        from docx import Document
        for key in ["word_path", "pdf_path"]:
            self.assertIn("_文献七_", Path(state[key]).name)
        self.assertEqual(Path(state["word_path"]).parent.name, "简读")
        item = wf.read_json(self.work / "zotero.json")
        self.assertIn("<h1>文献七｜要点｜虚构土壤研究（Test Journal 2024）</h1>", item["notes"][0]["note"])
        self.assertTrue(item["id"])
        document = Document(state["word_path"])
        self.assertFalse(document.styles._element.xpath(".//w:pBdr"))

    def test_duplicate_doi_does_not_overwrite(self):
        state = self.prepare()
        before = Path(state["pdf_path"]).read_bytes()
        self.data["number"] = 8
        self.data["doi"] = "https://doi.org/10.0000/TEST"
        wf.write_json(self.paper, self.data)
        with self.assertRaisesRegex(ValueError, "already exists"):
            wf.prepare(self.config, self.paper, self.pdf, self.base / "other")
        self.assertEqual(before, Path(state["pdf_path"]).read_bytes())

    def test_number_collision(self):
        self.prepare()
        self.data.update(doi="10.0000/another", title="Another Synthetic Study")
        wf.write_json(self.paper, self.data)
        with self.assertRaisesRegex(ValueError, "number already"):
            wf.prepare(self.config, self.paper, self.pdf, self.base / "other")

    def test_html_is_rejected(self):
        self.pdf.write_bytes(b"<html>login required</html>")
        with self.assertRaisesRegex(ValueError, "not a PDF"):
            self.prepare()

    def test_output_escape_rejected(self):
        wf.write_json(self.config, {"paper_root": "papers", "pdf_subdir": "../outside"})
        with self.assertRaisesRegex(ValueError, "inside paper_root"):
            self.prepare()

    def test_import_preview_has_no_writes(self):
        self.prepare()
        with patch.object(wf, "connector", return_value=self.selected()) as api:
            result = wf.import_zotero(self.work)
        self.assertEqual([x.args[0] for x in api.call_args_list], ["getSelectedCollection"])
        self.assertFalse(result["writes"])

    def test_import_uses_parent_id_and_is_idempotent(self):
        self.prepare()
        def api(endpoint, *args, **kwargs):
            return self.selected() if endpoint == "getSelectedCollection" else {}
        with patch.object(wf, "connector", side_effect=api) as calls:
            wf.import_zotero(self.work, True)
            count = calls.call_count
            wf.import_zotero(self.work, True)
            self.assertEqual(count, calls.call_count)
        saved = next(c for c in calls.call_args_list if c.args[0] == "saveItems")
        attach = next(c for c in calls.call_args_list if c.args[0] == "saveAttachment")
        self.assertEqual(saved.args[1]["items"][0]["id"], attach.kwargs["metadata"]["parentItemID"])

    def test_classification_failure_resumes_without_duplicate(self):
        self.prepare()
        def first(endpoint, *args, **kwargs):
            if endpoint == "updateSession":
                raise ConnectionError("synthetic failure")
            return self.selected() if endpoint == "getSelectedCollection" else {}
        with patch.object(wf, "connector", side_effect=first):
            with self.assertRaises(ConnectionError):
                wf.import_zotero(self.work, True)
        self.assertEqual(wf.read_json(self.work / "manifest.json")["stage"], "item_saved")
        with patch.object(wf, "connector", side_effect=lambda endpoint, *a, **k: self.selected() if endpoint == "getSelectedCollection" else {}) as calls:
            wf.import_zotero(self.work, True)
        self.assertNotIn("saveItems", [c.args[0] for c in calls.call_args_list])

    def test_uncertain_attachment_is_not_retried(self):
        self.prepare()
        def api(endpoint, *args, **kwargs):
            if endpoint == "saveAttachment":
                raise TimeoutError("synthetic timeout after send")
            return self.selected() if endpoint == "getSelectedCollection" else {}
        with patch.object(wf, "connector", side_effect=api):
            with self.assertRaises(TimeoutError):
                wf.import_zotero(self.work, True)
        with patch.object(wf, "connector") as calls:
            with self.assertRaisesRegex(RuntimeError, "uncertain"):
                wf.import_zotero(self.work, True)
        calls.assert_not_called()

    def test_changed_pdf_rejected_before_network(self):
        state = self.prepare()
        with Path(state["pdf_path"]).open("ab") as f:
            f.write(b"\n%changed\n")
        with patch.object(wf, "connector") as calls:
            with self.assertRaisesRegex(ValueError, "PDF changed"):
                wf.import_zotero(self.work, True)
        calls.assert_not_called()


    def test_cross_discipline_and_theoretical_sections(self):
        for index, discipline in enumerate(["医学", "计算机", "材料", "经济", "数学", "人文"], 1):
            with self.subTest(discipline=discipline):
                self.data.update(number=index, title="Synthetic " + discipline,
                                 title_zh=discipline + "虚构研究", doi="10.0000/example" + str(index),
                                 sections=[{"heading": "论证与证据", "text": "仅用虚构材料检查归档，不要求实验样本量。"}])
                wf.write_json(self.paper, self.data)
                wf.write_json(self.config, {"paper_root": "papers", "collection_name": discipline,
                                           "discipline": discipline, "research_focus": "测试主题"})
                work = self.base / ("task-" + str(index))
                result = wf.prepare(self.config, self.paper, self.pdf, work)
                self.assertEqual(result["collection_name"], discipline)
                item = wf.read_json(work / "zotero.json")
                self.assertIn(discipline + "虚构研究", item["notes"][0]["note"])
                self.assertTrue(Path(result["word_path"]).exists())


if __name__ == "__main__":
    unittest.main()
