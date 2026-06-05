-- AI Band: refresh the current response MIDI onto existing instrument tracks.
-- Run this after python -m ai_band.respond writes examples/ai-feedback-response.mid.

local DEFAULT_MIDI = "\\\\dees-workbench\\cloud-mirror\\ai-band\\examples\\ai-feedback-response.mid"

local TARGET_TRACKS = {
  ["AI Drummer"] = true,
  ["AI Bass Player"] = true,
  ["AI Guitar Player"] = true,
  ["AI Keyboard Player"] = true,
  ["AI Lead Player"] = true,
  ["AI Percussion Extras"] = true,
}

local function file_exists(path)
  local file = io.open(path, "rb")
  if file then
    file:close()
    return true
  end
  return false
end

local function track_name(track)
  local ok, name = reaper.GetSetMediaTrackInfo_String(track, "P_NAME", "", false)
  if ok then return name end
  return ""
end

local function snapshot_track_guids()
  local guids = {}
  for index = 0, reaper.CountTracks(0) - 1 do
    local track = reaper.GetTrack(0, index)
    guids[reaper.GetTrackGUID(track)] = true
  end
  return guids
end

local function collect_target_tracks()
  local tracks = {}
  for index = 0, reaper.CountTracks(0) - 1 do
    local track = reaper.GetTrack(0, index)
    local name = track_name(track)
    if TARGET_TRACKS[name] and tracks[name] == nil then
      tracks[name] = track
    end
  end
  return tracks
end

local function collect_new_tracks(before_guids)
  local tracks = {}
  for index = 0, reaper.CountTracks(0) - 1 do
    local track = reaper.GetTrack(0, index)
    if before_guids[reaper.GetTrackGUID(track)] == nil then
      table.insert(tracks, track)
    end
  end
  return tracks
end

local function clear_items(track)
  for item_index = reaper.CountTrackMediaItems(track) - 1, 0, -1 do
    local item = reaper.GetTrackMediaItem(track, item_index)
    reaper.DeleteTrackMediaItem(track, item)
  end
end

local function move_items(source_track, target_track)
  local moved = 0
  for item_index = reaper.CountTrackMediaItems(source_track) - 1, 0, -1 do
    local item = reaper.GetTrackMediaItem(source_track, item_index)
    reaper.MoveMediaItemToTrack(item, target_track)
    moved = moved + 1
  end
  return moved
end

local function delete_tracks(tracks)
  for index = #tracks, 1, -1 do
    reaper.DeleteTrack(tracks[index])
  end
end

local midi_path = DEFAULT_MIDI
if not file_exists(midi_path) then
  local ok, selected = reaper.GetUserFileNameForRead("", "Refresh AI Band response MIDI", ".mid")
  if not ok then return end
  midi_path = selected
end

local target_tracks = collect_target_tracks()
local target_count = 0
for _, _ in pairs(target_tracks) do
  target_count = target_count + 1
end

reaper.Undo_BeginBlock()
reaper.PreventUIRefresh(1)

local old_cursor = reaper.GetCursorPosition()
local before_guids = snapshot_track_guids()
reaper.SetEditCurPos(0, false, false)
reaper.InsertMedia(midi_path, 0)

local imported_tracks = collect_new_tracks(before_guids)
local moved_count = 0
local refreshed_count = 0
local delete_imported = {}

if target_count > 0 then
  for _, imported_track in ipairs(imported_tracks) do
    local name = track_name(imported_track)
    local target_track = target_tracks[name]
    if target_track ~= nil then
      clear_items(target_track)
      moved_count = moved_count + move_items(imported_track, target_track)
      refreshed_count = refreshed_count + 1
      table.insert(delete_imported, imported_track)
    elseif name:find("Bandleader") ~= nil or name == "" then
      table.insert(delete_imported, imported_track)
    end
  end
  delete_tracks(delete_imported)
end

reaper.SetEditCurPos(old_cursor, false, false)
reaper.PreventUIRefresh(-1)
reaper.UpdateArrange()
reaper.Undo_EndBlock("Refresh AI Band response MIDI", -1)

if target_count == 0 then
  reaper.ShowMessageBox("Imported response MIDI as new tracks. Existing AI Band instrument tracks were not found yet.", "AI Band", 0)
else
  reaper.ShowMessageBox(
    "Refreshed " .. refreshed_count .. " AI Band tracks from:\n" .. midi_path .. "\n\nMoved MIDI items: " .. moved_count .. "\nExisting instruments and FX were kept.",
    "AI Band",
    0
  )
end
