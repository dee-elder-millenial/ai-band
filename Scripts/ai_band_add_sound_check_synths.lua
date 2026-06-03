-- AI Band: add simple built-in ReaSynth instruments for MIDI sound-checking.
-- This is only an audition helper. It is not the final tone layer.

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
    local fx_index = reaper.TrackFX_AddByName(track, "ReaSynth", false, -1)
    if fx_index >= 0 then
      reaper.TrackFX_SetParam(track, fx_index, 0, 0.12)
      reaper.TrackFX_SetParam(track, fx_index, 1, 0.30)
      reaper.TrackFX_SetParam(track, fx_index, 2, 0.40)
      reaper.TrackFX_SetParam(track, fx_index, 3, 0.20)
      changed = changed + 1
    end
  end
end

reaper.Undo_EndBlock("Add AI Band sound-check synths", -1)
reaper.ShowMessageBox("Added ReaSynth to " .. changed .. " AI Band MIDI tracks.", "AI Band", 0)

