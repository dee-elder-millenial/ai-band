-- AI Band: one-click import, rough-tone setup, and starter FX for Main Street Thunder.

local DEFAULT_MIDI = "\\\\dees-workbench\\cloud-mirror\\ai-band\\examples\\main-street-thunder.mid"

local script_path = ({reaper.get_action_context()})[2]:match("^(.*)[/\\]")
package.path = script_path .. "/?.lua;" .. package.path
local helpers = require("ai_band_tone_helpers")

local function file_exists(path)
  local file = io.open(path, "rb")
  if file then
    file:close()
    return true
  end
  return false
end

local midi_path = DEFAULT_MIDI
if not file_exists(midi_path) then
  local ok, selected = reaper.GetUserFileNameForRead("", "Import AI Band Main Street Thunder MIDI", ".mid")
  if not ok then return end
  midi_path = selected
end

reaper.Undo_BeginBlock()
reaper.SetEditCurPos(0, false, false)
reaper.InsertMedia(midi_path, 0)
local configured, added = helpers.configure_rough_tones()
local fx_configured, fx_added = helpers.configure_rough_effects()
reaper.GetSetProjectInfo_String(0, "PROJECT_NAME", "AI Band - Main Street Thunder", true)
reaper.Undo_EndBlock("Set up Main Street Thunder audition", -1)

reaper.ShowMessageBox(
  "Imported Main Street Thunder.\n\nThe MIDI includes a subtle 117-119 BPM tempo feel map.\n\nTone tracks configured: " .. configured ..
  "\nInstruments added: " .. added ..
  "\nFX configured: " .. fx_configured ..
  "\nFX added: " .. fx_added ..
  "\n\nIf drums are silent, open MT-PowerDrumKit on AI Drummer and click its start/activation button.",
  "AI Band",
  0
)
