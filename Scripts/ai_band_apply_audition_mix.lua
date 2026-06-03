-- AI Band: apply current rough tone, balance, pan, and starter FX defaults.
-- Run this on an already-imported AI Band REAPER project without reimporting MIDI.

local script_path = ({reaper.get_action_context()})[2]:match("^(.*)[/\\]")
package.path = script_path .. "/?.lua;" .. package.path
local helpers = require("ai_band_tone_helpers")

reaper.Undo_BeginBlock()
local tone_configured, instruments_added = helpers.configure_rough_tones()
local fx_configured, fx_added = helpers.configure_rough_effects()
reaper.Undo_EndBlock("Apply AI Band audition mix", -1)

reaper.ShowMessageBox(
  "Applied AI Band audition mix.\n\nTone tracks configured: " .. tone_configured ..
  "\nInstruments added: " .. instruments_added ..
  "\nFX configured: " .. fx_configured ..
  "\nFX added: " .. fx_added ..
  "\n\nUse this after changing instruments or when the mix starts feeling too loud, dry, or crowded.",
  "AI Band",
  0
)
