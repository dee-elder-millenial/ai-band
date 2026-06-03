-- AI Band: one-click import and rough-tone setup for Hard Flag Blues with AI rhythm guitar.

local DEFAULT_MIDI = "\\\\dees-workbench\\cloud-mirror\\ai-band\\examples\\hard-flag-blues-with-rhythm-guitar.mid"

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
  local ok, selected = reaper.GetUserFileNameForRead("", "Import AI Band Hard Flag Blues With Guitar MIDI", ".mid")
  if not ok then return end
  midi_path = selected
end

reaper.Undo_BeginBlock()
reaper.InsertMedia(midi_path, 0)
local configured, added = helpers.configure_rough_tones()
reaper.GetSetProjectInfo_String(0, "PROJECT_NAME", "AI Band - Hard Flag Blues With AI Rhythm Guitar", true)
reaper.Undo_EndBlock("Set up Hard Flag Blues with AI rhythm guitar audition", -1)

reaper.ShowMessageBox("Imported Hard Flag Blues with AI rhythm guitar and configured " .. configured .. " tone tracks. Added " .. added .. " instruments.", "AI Band", 0)
