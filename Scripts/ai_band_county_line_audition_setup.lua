-- AI Band: one-click import and rough-tone setup for the County Line Ghosts sketch.

local DEFAULT_MIDI = "\\\\dees-workbench\\cloud-mirror\\ai-band\\examples\\county-line-ghosts.mid"

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
  local ok, selected = reaper.GetUserFileNameForRead("", "Import AI Band County Line Ghosts MIDI", ".mid")
  if not ok then return end
  midi_path = selected
end

reaper.Undo_BeginBlock()
reaper.InsertMedia(midi_path, 0)
local configured, added = helpers.configure_rough_tones()
reaper.GetSetProjectInfo_String(0, "PROJECT_NAME", "AI Band - County Line Ghosts", true)
reaper.Undo_EndBlock("Set up County Line Ghosts audition", -1)

reaper.ShowMessageBox("Imported County Line Ghosts and configured " .. configured .. " tone tracks. Added " .. added .. " instruments.", "AI Band", 0)

