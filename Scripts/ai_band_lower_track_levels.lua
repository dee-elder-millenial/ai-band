-- AI Band: lower imported MIDI track levels for safer auditioning.

local TRACK_VOLUME = 0.18
local TRACK_PANS = {
  ["AI Drummer"] = 0.0,
  ["AI Bass Player"] = 0.0,
  ["AI Guitar Player"] = -0.35,
  ["AI Keyboard Player"] = 0.35,
  ["AI Lead Player"] = 0.12,
  ["AI Percussion Extras"] = -0.12,
}

local function track_name(track)
  local ok, name = reaper.GetSetMediaTrackInfo_String(track, "P_NAME", "", false)
  if ok then
    return name
  end
  return ""
end

local function should_skip(name)
  return name == "" or name:find("Bandleader") ~= nil
end

local changed = 0

reaper.Undo_BeginBlock()

for index = 0, reaper.CountTracks(0) - 1 do
  local track = reaper.GetTrack(0, index)
  local name = track_name(track)

  if not should_skip(name) then
    reaper.SetMediaTrackInfo_Value(track, "D_VOL", TRACK_VOLUME)
    reaper.SetMediaTrackInfo_Value(track, "D_PAN", TRACK_PANS[name] or 0.0)
    changed = changed + 1
  end
end

reaper.Undo_EndBlock("Lower AI Band track levels", -1)
reaper.ShowMessageBox("Lowered " .. changed .. " AI Band track levels.", "AI Band", 0)
