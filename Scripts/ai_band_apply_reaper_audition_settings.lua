-- AI Band: apply project-level REAPER audition settings.
-- Run this after importing an AI Band MIDI sketch, then run ai_band_apply_audition_mix.lua.

local function find_fx(track, needle)
  for index = 0, reaper.TrackFX_GetCount(track) - 1 do
    local ok, fx_name = reaper.TrackFX_GetFXName(track, index, "")
    if ok and fx_name:find(needle) ~= nil then
      return index
    end
  end
  return -1
end

local function set_param_by_name(track, fx_index, needles, value)
  local param_count = reaper.TrackFX_GetNumParams(track, fx_index)
  for param = 0, param_count - 1 do
    local ok, param_name = reaper.TrackFX_GetParamName(track, fx_index, param, "")
    if ok then
      local lower_name = param_name:lower()
      for _, needle in ipairs(needles) do
        if lower_name:find(needle) then
          reaper.TrackFX_SetParamNormalized(track, fx_index, param, value)
          return true
        end
      end
    end
  end
  return false
end

local function add_master_limiter(master)
  local fx_index = find_fx(master, "ReaLimit")
  if fx_index < 0 then
    fx_index = reaper.TrackFX_AddByName(master, "ReaLimit (Cockos)", false, -1)
  end
  if fx_index < 0 then
    return false
  end

  set_param_by_name(master, fx_index, {"threshold"}, 0.70)
  set_param_by_name(master, fx_index, {"ceiling"}, 0.82)
  set_param_by_name(master, fx_index, {"release"}, 0.35)
  return true
end

reaper.Undo_BeginBlock()

local master = reaper.GetMasterTrack(0)
reaper.SetMediaTrackInfo_Value(master, "D_VOL", 0.82)
if reaper.CSurf_OnPlayRateChange then
  reaper.CSurf_OnPlayRateChange(1.0)
end

local limiter_ok = add_master_limiter(master)

reaper.Undo_EndBlock("Apply AI Band REAPER audition settings", -1)

local limiter_status = "Master limiter added/configured."
if not limiter_ok then
  limiter_status = "ReaLimit was not found; manually add a gentle limiter on the master if the mix clips."
end

reaper.ShowMessageBox(
  "Applied AI Band REAPER audition settings.\n\n" ..
  "Master fader set below unity.\n" ..
  "Playback rate reset to 1.0.\n" ..
  limiter_status .. "\n\n" ..
  "Next: run ai_band_apply_audition_mix.lua and try warmer-room or lead-back.",
  "AI Band",
  0
)
