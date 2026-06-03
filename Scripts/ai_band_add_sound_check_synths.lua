-- AI Band: add simple built-in ReaSynth instruments for MIDI sound-checking.
-- This is only an audition helper. It is not the final tone layer.

local DEFAULT_TRACK_VOLUME = 0.16
local TRACK_VOLUMES = {
  ["AI Drummer"] = 0.28,
  ["AI Bass Player"] = 0.18,
  ["AI Guitar Player"] = 0.14,
  ["AI Keyboard Player"] = 0.10,
  ["AI Lead Player"] = 0.16,
  ["AI Percussion Extras"] = 0.11,
}
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

local function find_reasynth(track)
  for index = 0, reaper.TrackFX_GetCount(track) - 1 do
    local ok, fx_name = reaper.TrackFX_GetFXName(track, index, "")
    if ok and fx_name:find("ReaSynth") ~= nil then
      return index
    end
  end
  return -1
end

local function set_quiet_reasynth(track, fx_index)
  -- These values are deliberately conservative; this script is only
  -- for confirming MIDI playback without clipping the master bus.
  reaper.TrackFX_SetParam(track, fx_index, 0, 0.04)
  reaper.TrackFX_SetParam(track, fx_index, 1, 0.15)
  reaper.TrackFX_SetParam(track, fx_index, 2, 0.15)
  reaper.TrackFX_SetParam(track, fx_index, 3, 0.08)
end

local changed = 0
local leveled = 0
local cooled = 0

reaper.Undo_BeginBlock()

for index = 0, reaper.CountTracks(0) - 1 do
  local track = reaper.GetTrack(0, index)
  local name = track_name(track)

  if not should_skip(name) then
    reaper.SetMediaTrackInfo_Value(track, "D_VOL", TRACK_VOLUMES[name] or DEFAULT_TRACK_VOLUME)
    reaper.SetMediaTrackInfo_Value(track, "D_PAN", TRACK_PANS[name] or 0.0)
    leveled = leveled + 1

    local fx_index = find_reasynth(track)
    if fx_index < 0 then
      fx_index = reaper.TrackFX_AddByName(track, "ReaSynth", false, -1)
      if fx_index >= 0 then
        changed = changed + 1
      end
    end
    if fx_index >= 0 then
      set_quiet_reasynth(track, fx_index)
      cooled = cooled + 1
    end
  end
end

reaper.Undo_EndBlock("Add AI Band sound-check synths", -1)
reaper.ShowMessageBox("Leveled " .. leveled .. " tracks, cooled " .. cooled .. " synths, and added ReaSynth to " .. changed .. " AI Band MIDI tracks.", "AI Band", 0)
