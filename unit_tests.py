import unittest
from unittest.mock import MagicMock, patch
from main import analyze_pdf

class TestAnalyzePDF(unittest.TestCase):

    @patch('main.fitz.open')
    def test_protection_class_I_valid_rpe(self, mock_fitz_open):
        mock_page = MagicMock()
        mock_page.get_text.return_value = (
            "12345\n"
            "Název: Spotřebič XYZ\n"
            "Třída ochrany: I\n"
            "Rpe: 0,20 Ω\n"
            "RisoM-PE: >1,2 MΩ\n"
            "IaltEq: 3,0\n"
            "IdirTouch: 0,3\n"
            "reverzní: 0,2\n"
        )
        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc

        result = analyze_pdf("dummy_path.pdf")
        joined = "\n".join(result)

        self.assertIn("✅ 12345: Rpe = 0.2 Ω (v normě)", joined)
        self.assertIn("✅ 12345: RisoM-PE = 1.2 MΩ (v pořádku)", joined)
        self.assertIn("✅ 12345: IaltEq = 3.0 mA (v normě)", joined)
        self.assertIn("✅ 12345: IdirTouch = 0.3 mA (v normě)", joined)
        self.assertIn("✅ 12345: IdirTouch (reverzní) = 0.2 mA (v normě)", joined)

    @patch('main.fitz.open')
    def test_missing_protection_class(self, mock_fitz_open):
        mock_page = MagicMock()
        mock_page.get_text.return_value = (
            "999\n"
            "Název: Něco\n"
            "Rpe: 0,25 Ω\n"
        )
        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc

        result = analyze_pdf("dummy.pdf")
        joined = "\n".join(result)
        self.assertIn("⚠️ 999: Třída ochrany nebyla nalezena", joined)

    @patch('main.fitz.open')
    def test_device_is_class_II(self, mock_fitz_open):
        mock_page = MagicMock()
        mock_page.get_text.return_value = (
            "555\n"
            "Název: Něco\n"
            "Třída ochrany: II\n"
        )
        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc

        result = analyze_pdf("dummy.pdf")
        self.assertTrue(any("Třída ochrany II – měření Rpe není požadováno" in line for line in result))

    @patch('main.fitz.open')
    def test_selv_pelv_out_of_range(self, mock_fitz_open):
        mock_page = MagicMock()
        mock_page.get_text.return_value = (
            "1\n"
            "Název: Síťový adaptér 5V XYZ\n"
            "Třída ochrany: I\n"
            "Napětí zdroje SELV/PELV U: 5,5\n"
        )
        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc

        result = analyze_pdf("dummy.pdf")
        joined = "\n".join(result)
        self.assertIn("mimo rozsah 4,75–5,25 V", joined)

if __name__ == '__main__':
    unittest.main()
