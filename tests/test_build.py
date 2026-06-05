from __future__ import annotations

import unittest

from ai_band import build


class BuildPackageTests(unittest.TestCase):
    def test_build_manifest_reaper_entrypoints_exist(self) -> None:
        manifest = build.build_manifest(ticks_per_beat=480, tempo_bpm=108)
        reaper = manifest["reaper"]

        self.assertEqual(reaper["audition_mix_script"], "Scripts/ai_band_apply_audition_mix.lua")
        self.assertEqual(reaper["reaper_audition_settings_script"], "Scripts/ai_band_apply_reaper_audition_settings.lua")
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

    def test_reaper_audition_settings_script_sets_safe_project_defaults(self) -> None:
        script = (build.REPO_ROOT / "Scripts" / "ai_band_apply_reaper_audition_settings.lua").read_text(encoding="utf-8")

        self.assertIn("CSurf_OnPlayRateChange(1.0)", script)
        self.assertIn("ReaLimit", script)
        self.assertIn('SetMediaTrackInfo_Value(master, "D_VOL", 0.82)', script)

    def test_live_cue_script_stamps_cues_to_timeline_track(self) -> None:
        script = (build.REPO_ROOT / "Scripts" / "ai_band_write_live_cue.lua").read_text(encoding="utf-8")

        self.assertIn("AI Live Cues", script)
        self.assertIn("AddMediaItemToTrack", script)
        self.assertIn("AddProjectMarker2", script)
        self.assertIn("is_playing", script)
        self.assertIn("cue_id", script)

    def test_live_response_refresh_script_preserves_instrument_tracks(self) -> None:
        script = (build.REPO_ROOT / "Scripts" / "ai_band_refresh_response_midi.lua").read_text(encoding="utf-8")

        self.assertIn("ai-feedback-response.mid", script)
        self.assertIn("MoveMediaItemToTrack", script)
        self.assertIn("DeleteTrackMediaItem", script)
        self.assertIn("Existing instruments and FX were kept", script)

    def test_status_and_handoff_docs_exist(self) -> None:
        for relative_path in ("docs/PROJECT_DASHBOARD.md", "docs/HANDOFF.md"):
            with self.subTest(path=relative_path):
                text = (build.REPO_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn("AI Band", text)


if __name__ == "__main__":
    unittest.main()
