from __future__ import annotations

import unittest

from ai_band import build


class BuildPackageTests(unittest.TestCase):
    def test_build_manifest_reaper_entrypoints_exist(self) -> None:
        manifest = build.build_manifest(ticks_per_beat=480, tempo_bpm=108)
        reaper = manifest["reaper"]

        self.assertEqual(reaper["audition_mix_script"], "Scripts/ai_band_apply_audition_mix.lua")
        for relative_path in reaper.values():
            with self.subTest(path=relative_path):
                self.assertTrue((build.REPO_ROOT / relative_path).exists(), relative_path)

    def test_audition_mix_script_prompts_for_profiles(self) -> None:
        script = (build.REPO_ROOT / "Scripts" / "ai_band_apply_audition_mix.lua").read_text(encoding="utf-8")
        helper = (build.REPO_ROOT / "Scripts" / "ai_band_tone_helpers.lua").read_text(encoding="utf-8")

        self.assertIn("reaper.GetUserInputs", script)
        self.assertIn("helpers.apply_mix_profile", script)
        for profile in ("balanced", "drums-forward", "warmer-room", "lead-back"):
            with self.subTest(profile=profile):
                self.assertIn(profile, helper)


if __name__ == "__main__":
    unittest.main()
