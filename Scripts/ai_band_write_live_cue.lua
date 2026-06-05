-- AI Band: write a live instruction cue for the bandleader/generator.

local DEFAULT_CUE = "\\\\dees-workbench\\cloud-mirror\\ai-band\\state\\live_cue.json"

local ok, values = reaper.GetUserInputs(
  "AI Band Cue",
  3,
  "Instruction,Target,Intensity 0-1",
  "simplify bass,bandleader,0.5"
)

if not ok then return end

local instruction, target, intensity = values:match("([^,]*),([^,]*),([^,]*)")
instruction = instruction or ""
target = target or "bandleader"
intensity = tonumber(intensity) or 0.5

local _, project_path = reaper.EnumProjects(-1, "")
local play_position = reaper.GetPlayPosition()
local play_state = reaper.GetPlayState()
local is_playing = (play_state & 1) == 1
local cue_id = tostring(os.time()) .. "-" .. tostring(math.floor(play_position * 1000))

local function escape_json(value)
  value = value:gsub("\\", "\\\\")
  value = value:gsub("\"", "\\\"")
  value = value:gsub("\n", "\\n")
  value = value:gsub("\r", "\\r")
  return value
end

local json = "{\n"
  .. "  \"mode\": \"live-cue\",\n"
  .. "  \"instruction\": \"" .. escape_json(instruction) .. "\",\n"
  .. "  \"target\": \"" .. escape_json(target) .. "\",\n"
  .. "  \"intensity\": " .. string.format("%.3f", intensity) .. ",\n"
  .. "  \"play_position_seconds\": " .. string.format("%.3f", play_position) .. ",\n"
  .. "  \"is_playing\": " .. (is_playing and "true" or "false") .. ",\n"
  .. "  \"cue_id\": \"" .. escape_json(cue_id) .. "\",\n"
  .. "  \"project_path\": \"" .. escape_json(project_path or "") .. "\"\n"
  .. "}\n"

local file = io.open(DEFAULT_CUE, "w")
if not file then
  reaper.ShowMessageBox("Could not write cue file:\n" .. DEFAULT_CUE, "AI Band", 0)
  return
end

file:write(json)
file:close()

local function track_name(track)
  local ok_name, name = reaper.GetSetMediaTrackInfo_String(track, "P_NAME", "", false)
  if ok_name then return name end
  return ""
end

local function find_or_create_cue_track()
  for index = 0, reaper.CountTracks(0) - 1 do
    local track = reaper.GetTrack(0, index)
    if track_name(track) == "AI Live Cues" then
      return track
    end
  end

  local index = reaper.CountTracks(0)
  reaper.InsertTrackAtIndex(index, true)
  local track = reaper.GetTrack(0, index)
  reaper.GetSetMediaTrackInfo_String(track, "P_NAME", "AI Live Cues", true)
  reaper.SetMediaTrackInfo_Value(track, "D_VOL", 0.0)
  reaper.SetMediaTrackInfo_Value(track, "B_MUTE", 1)
  return track
end

local function write_cue_to_track()
  local cue_track = find_or_create_cue_track()
  if not cue_track then return false end

  local item = reaper.AddMediaItemToTrack(cue_track)
  if not item then return false end

  local item_length = 2.0
  reaper.SetMediaItemInfo_Value(item, "D_POSITION", play_position)
  reaper.SetMediaItemInfo_Value(item, "D_LENGTH", item_length)
  reaper.GetSetMediaItemInfo_String(item, "P_NOTES", instruction .. "\nTarget: " .. target .. "\nIntensity: " .. string.format("%.2f", intensity), true)

  local take = reaper.AddTakeToMediaItem(item)
  if take then
    reaper.GetSetMediaItemTakeInfo_String(take, "P_NAME", instruction, true)
  end

  local marker_name = "AI Cue: " .. instruction
  reaper.AddProjectMarker2(0, false, play_position, 0, marker_name, -1, 0)
  return true
end

reaper.Undo_BeginBlock()
local wrote_track = write_cue_to_track()
reaper.UpdateArrange()
reaper.Undo_EndBlock("Write AI Band live cue", -1)

local message = "Wrote AI Band cue JSON:\n" .. instruction
if wrote_track then
  message = message .. "\n\nStamped cue to AI Live Cues at " .. string.format("%.2f", play_position) .. " seconds."
else
  message = message .. "\n\nCould not stamp cue to AI Live Cues track."
end

reaper.ShowMessageBox(message, "AI Band", 0)
