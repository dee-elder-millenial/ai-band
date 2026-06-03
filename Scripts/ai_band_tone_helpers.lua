-- Shared AI Band REAPER helper functions.

local M = {}

M.DEFAULT_TRACK_VOLUME = 0.14
M.TRACK_VOLUMES = {
  ["AI Drummer"] = 0.30,
  ["AI Bass Player"] = 0.16,
  ["AI Guitar Player"] = 0.12,
  ["AI Keyboard Player"] = 0.09,
  ["AI Lead Player"] = 0.15,
  ["AI Percussion Extras"] = 0.10,
}
M.TRACK_PANS = {
  ["AI Drummer"] = 0.0,
  ["AI Bass Player"] = 0.0,
  ["AI Guitar Player"] = -0.32,
  ["AI Keyboard Player"] = 0.32,
  ["AI Lead Player"] = 0.10,
  ["AI Percussion Extras"] = -0.12,
}
M.PREFERRED_INSTRUMENTS = {
  ["AI Drummer"] = {
    name = "VST3i: MT-PowerDrumKit (MANDA AUDIO) (16 out)",
    needle = "MT%-PowerDrumKit",
    fallback_name = "JS: AI Band GM Drum Synth",
    fallback_needle = "AI Band GM Drum Synth",
  },
  ["AI Percussion Extras"] = {
    name = "VST3i: MT-PowerDrumKit (MANDA AUDIO) (16 out)",
    needle = "MT%-PowerDrumKit",
    fallback_name = "JS: AI Band GM Drum Synth",
    fallback_needle = "AI Band GM Drum Synth",
  },
  ["AI Bass Player"] = {
    name = "VSTi: Ample Bass P Lite II (Ample Sound)",
    needle = "Ample Bass P Lite II",
    fallback_name = "ReaSynth",
    fallback_needle = "ReaSynth",
  },
  ["AI Keyboard Player"] = {
    name = "VST3i: Splice INSTRUMENT (Splice)",
    needle = "Splice INSTRUMENT",
    fallback_name = "ReaSynth",
    fallback_needle = "ReaSynth",
  },
  ["AI Lead Player"] = {
    name = "VSTi: Ample Guitar M II Lite (Ample Sound)",
    needle = "Ample Guitar M II Lite",
    fallback_name = "ReaSynth",
    fallback_needle = "ReaSynth",
  },
  ["AI Guitar Player"] = {
    name = "VSTi: Ample Guitar M II Lite (Ample Sound)",
    needle = "Ample Guitar M II Lite",
    fallback_name = "ReaSynth",
    fallback_needle = "ReaSynth",
  },
}
M.TRACK_EFFECTS = {
  ["AI Drummer"] = {
    {name = "ReaComp (Cockos)", needle = "ReaComp"},
    {name = "ReaVerbate (Cockos)", needle = "ReaVerbate"},
  },
  ["AI Bass Player"] = {
    {name = "ReaComp (Cockos)", needle = "ReaComp"},
  },
  ["AI Guitar Player"] = {
    {name = "ReaComp (Cockos)", needle = "ReaComp"},
    {name = "ReaVerbate (Cockos)", needle = "ReaVerbate"},
  },
  ["AI Keyboard Player"] = {
    {name = "ReaComp (Cockos)", needle = "ReaComp"},
    {name = "ReaVerbate (Cockos)", needle = "ReaVerbate"},
  },
  ["AI Lead Player"] = {
    {name = "ReaComp (Cockos)", needle = "ReaComp"},
    {name = "ReaVerbate (Cockos)", needle = "ReaVerbate"},
  },
  ["AI Percussion Extras"] = {
    {name = "ReaVerbate (Cockos)", needle = "ReaVerbate"},
  },
}
M.EFFECT_WET_MIX = {
  ["AI Drummer"] = {
    ["ReaComp"] = 0.70,
    ["ReaVerbate"] = 0.08,
  },
  ["AI Bass Player"] = {
    ["ReaComp"] = 0.62,
  },
  ["AI Guitar Player"] = {
    ["ReaComp"] = 0.58,
    ["ReaVerbate"] = 0.14,
  },
  ["AI Keyboard Player"] = {
    ["ReaComp"] = 0.48,
    ["ReaVerbate"] = 0.18,
  },
  ["AI Lead Player"] = {
    ["ReaComp"] = 0.52,
    ["ReaVerbate"] = 0.16,
  },
  ["AI Percussion Extras"] = {
    ["ReaVerbate"] = 0.10,
  },
}

function M.track_name(track)
  local ok, name = reaper.GetSetMediaTrackInfo_String(track, "P_NAME", "", false)
  if ok then return name end
  return ""
end

function M.should_skip(name)
  return name == "" or name:find("Bandleader") ~= nil
end

function M.find_fx(track, needle)
  for index = 0, reaper.TrackFX_GetCount(track) - 1 do
    local ok, fx_name = reaper.TrackFX_GetFXName(track, index, "")
    if ok and fx_name:find(needle) ~= nil then
      return index
    end
  end
  return -1
end

function M.add_or_find_fx(track, name, needle)
  local fx_index = M.find_fx(track, needle)
  if fx_index >= 0 then return fx_index, false end
  fx_index = reaper.TrackFX_AddByName(track, name, false, -1)
  return fx_index, fx_index >= 0
end

function M.add_preferred_instrument(track, track_name_value)
  local preferred = M.PREFERRED_INSTRUMENTS[track_name_value]
  if not preferred then
    local fx_index, was_added = M.add_or_find_fx(track, "ReaSynth", "ReaSynth")
    return fx_index, was_added, "fallback"
  end

  local fx_index, was_added = M.add_or_find_fx(track, preferred.name, preferred.needle)
  if fx_index >= 0 then
    return fx_index, was_added, "preferred"
  end

  fx_index, was_added = M.add_or_find_fx(track, preferred.fallback_name, preferred.fallback_needle)
  return fx_index, was_added, "fallback"
end

function M.set_reasynth(track, fx_index, track_name_value)
  local volume = 0.04
  local attack = 0.10
  local decay = 0.24
  local sustain = 0.18

  if track_name_value == "AI Bass Player" then
    volume = 0.04
    attack = 0.03
    decay = 0.18
    sustain = 0.30
  elseif track_name_value == "AI Keyboard Player" then
    volume = 0.025
    attack = 0.35
    decay = 0.45
    sustain = 0.12
  elseif track_name_value == "AI Lead Player" then
    volume = 0.035
    attack = 0.08
    decay = 0.28
    sustain = 0.16
  elseif track_name_value == "AI Guitar Player" then
    volume = 0.03
    attack = 0.02
    decay = 0.16
    sustain = 0.10
  end

  reaper.TrackFX_SetParam(track, fx_index, 0, volume)
  reaper.TrackFX_SetParam(track, fx_index, 1, attack)
  reaper.TrackFX_SetParam(track, fx_index, 2, decay)
  reaper.TrackFX_SetParam(track, fx_index, 3, sustain)
end

function M.set_drum_synth(track, fx_index, track_name_value)
  reaper.TrackFX_SetParam(track, fx_index, 0, track_name_value == "AI Drummer" and 0.62 or 0.34)
  reaper.TrackFX_SetParam(track, fx_index, 1, 0.72)
  reaper.TrackFX_SetParam(track, fx_index, 2, 0.50)
  reaper.TrackFX_SetParam(track, fx_index, 3, track_name_value == "AI Drummer" and 0.24 or 0.15)
end

function M.configure_rough_tones()
  local added = 0
  local configured = 0

  for index = 0, reaper.CountTracks(0) - 1 do
    local track = reaper.GetTrack(0, index)
    local name = M.track_name(track)

    if not M.should_skip(name) then
      reaper.SetMediaTrackInfo_Value(track, "D_VOL", M.TRACK_VOLUMES[name] or M.DEFAULT_TRACK_VOLUME)
      reaper.SetMediaTrackInfo_Value(track, "D_PAN", M.TRACK_PANS[name] or 0.0)

      local fx_index, was_added, source = M.add_preferred_instrument(track, name)
      if fx_index >= 0 then
        if source == "fallback" and (name == "AI Drummer" or name == "AI Percussion Extras") then
          M.set_drum_synth(track, fx_index, name)
        elseif source == "fallback" then
          M.set_reasynth(track, fx_index, name)
        end
        configured = configured + 1
        if was_added then added = added + 1 end
      end
    end
  end

  return configured, added
end

function M.configure_rough_effects()
  local configured = 0
  local added = 0

  for index = 0, reaper.CountTracks(0) - 1 do
    local track = reaper.GetTrack(0, index)
    local name = M.track_name(track)
    local effects = M.TRACK_EFFECTS[name]

    if effects then
      for _, effect in ipairs(effects) do
        local fx_index, was_added = M.add_or_find_fx(track, effect.name, effect.needle)
        if fx_index >= 0 then
          M.set_effect_wet_mix(track, fx_index, name, effect.needle)
          configured = configured + 1
          if was_added then added = added + 1 end
        end
      end
    end
  end

  return configured, added
end

function M.set_effect_wet_mix(track, fx_index, track_name_value, effect_needle)
  if not reaper.TrackFX_SetWetDryMix then return end
  local track_settings = M.EFFECT_WET_MIX[track_name_value]
  if not track_settings then return end
  local wet_mix = track_settings[effect_needle]
  if wet_mix == nil then return end
  reaper.TrackFX_SetWetDryMix(track, fx_index, wet_mix)
end

return M
