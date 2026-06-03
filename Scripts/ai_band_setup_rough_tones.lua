-- AI Band: rough tone setup for auditioning generated MIDI.
-- This is warmer than the emergency ReaSynth sound-check, but still not final tone.

local script_path = ({reaper.get_action_context()})[2]:match("^(.*)[/\\]")
package.path = script_path .. "/?.lua;" .. package.path
local helpers = require("ai_band_tone_helpers")

reaper.Undo_BeginBlock()
local configured, added = helpers.configure_rough_tones()
reaper.Undo_EndBlock("Set up AI Band rough tones", -1)
reaper.ShowMessageBox("Configured " .. configured .. " AI Band tone tracks and added " .. added .. " instruments.", "AI Band", 0)
