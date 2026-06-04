-- AI Band: import one of the rhythm-guitar diagnostic variants and apply audition tones.

local VARIANTS = {
  ["1"] = {
    label = "current-strummer",
    path = "\\\\dees-workbench\\cloud-mirror\\ai-band\\examples\\rhythm-guitar-current-strummer.mid",
    mode = "Use Ample Strummer mode. Tests the current richer chord-block profile.",
  },
  ["2"] = {
    label = "simple-blocks",
    path = "\\\\dees-workbench\\cloud-mirror\\ai-band\\examples\\rhythm-guitar-simple-blocks.mid",
    mode = "Use Ample Strummer mode. Tests simpler chord recognition and register.",
  },
  ["3"] = {
    label = "internal-strum",
    path = "\\\\dees-workbench\\cloud-mirror\\ai-band\\examples\\rhythm-guitar-internal-strum.mid",
    mode = "Use Finger/non-Strummer mode. Tests MIDI-level strumming.",
  },
}

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

local function choose_variant()
  local ok, value = reaper.GetUserInputs(
    "AI Band Rhythm Guitar Diagnostic",
    1,
    "1 current, 2 simple, 3 internal",
    "2"
  )
  if not ok then return nil end
  value = (value or ""):gsub("^%s+", ""):gsub("%s+$", "")
  return VARIANTS[value] or VARIANTS["2"]
end

local variant = choose_variant()
if not variant then return end

local midi_path = variant.path
if not file_exists(midi_path) then
  local ok, selected = reaper.GetUserFileNameForRead("", "Import AI Band rhythm guitar diagnostic MIDI", ".mid")
  if not ok then return end
  midi_path = selected
end

reaper.Undo_BeginBlock()
reaper.SetEditCurPos(0, false, false)
reaper.InsertMedia(midi_path, 0)
local configured, added = helpers.configure_rough_tones()
local fx_configured, fx_added = helpers.configure_rough_effects()
reaper.GetSetProjectInfo_String(0, "PROJECT_NAME", "AI Band - Rhythm Guitar " .. variant.label, true)
reaper.Undo_EndBlock("Set up AI Band rhythm guitar diagnostic audition", -1)

reaper.ShowMessageBox(
  "Imported rhythm guitar diagnostic: " .. variant.label ..
  "\n\n" .. variant.mode ..
  "\n\nSolo AI Guitar Player first. Once it sounds normal, add bass and drums." ..
  "\n\nTone tracks configured: " .. configured ..
  "\nInstruments added: " .. added ..
  "\nFX configured: " .. fx_configured ..
  "\nFX added: " .. fx_added ..
  "\n\nIf drums are silent, open MT-PowerDrumKit on AI Drummer and click its start/activation button.",
  "AI Band",
  0
)
