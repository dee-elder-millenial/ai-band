-- Shared AI Band REAPER helper functions.

local M = {}

M.DEFAULT_TRACK_VOLUME = 0.14
M.TRACK_VOLUMES = {
  ["AI Drummer"] = 0.34,
  ["AI Bass Player"] = 0.13,
  ["AI Guitar Player"] = 0.13,
  ["AI Keyboard Player"] = 0.075,
  ["AI Lead Player"] = 0.13,
  ["AI Percussion Extras"] = 0.09,
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
M.EFFECT_PARAM_TARGETS = {
  ["AI Drummer"] = {
    ["ReaVerbate"] = {
      wet = 0.07,
      dry = 0.92,
      room = 0.30,
      damp = 0.58,
    },
  },
  ["AI Bass Player"] = {
    ["ReaComp"] = {
      wet = 0.90,
    },
  },
  ["AI Guitar Player"] = {
    ["ReaVerbate"] = {
      wet = 0.13,
      dry = 0.88,
      room = 0.42,
      damp = 0.46,
    },
  },
  ["AI Keyboard Player"] = {
    ["ReaVerbate"] = {
      wet = 0.17,
      dry = 0.84,
      room = 0.50,
      damp = 0.50,
    },
  },
  ["AI Lead Player"] = {
    ["ReaVerbate"] = {
      wet = 0.15,
      dry = 0.86,
      room = 0.45,
      damp = 0.44,
    },
  },
  ["AI Percussion Extras"] = {
    ["ReaVerbate"] = {
      wet = 0.10,
      dry = 0.88,
      room = 0.36,
      damp = 0.54,
    },
  },
}
M.MIX_PROFILE_NAMES = "balanced, drums-forward, warmer-room, lead-back"
M.MIX_PROFILES = {
  ["drums-forward"] = {
    volumes = {
      ["AI Drummer"] = 0.38,
      ["AI Bass Player"] = 0.12,
      ["AI Keyboard Player"] = 0.070,
      ["AI Lead Player"] = 0.12,
      ["AI Percussion Extras"] = 0.08,
    },
    effects = {
      ["AI Drummer"] = {
        ["ReaVerbate"] = {wet = 0.055, dry = 0.95, room = 0.26, damp = 0.62},
      },
    },
  },
  ["warmer-room"] = {
    volumes = {
      ["AI Guitar Player"] = 0.12,
      ["AI Keyboard Player"] = 0.070,
      ["AI Lead Player"] = 0.12,
    },
    effects = {
      ["AI Drummer"] = {
        ["ReaVerbate"] = {wet = 0.085, dry = 0.90, room = 0.34, damp = 0.58},
      },
      ["AI Guitar Player"] = {
        ["ReaVerbate"] = {wet = 0.18, dry = 0.84, room = 0.52, damp = 0.50},
      },
      ["AI Keyboard Player"] = {
        ["ReaVerbate"] = {wet = 0.22, dry = 0.80, room = 0.58, damp = 0.54},
      },
      ["AI Lead Player"] = {
        ["ReaVerbate"] = {wet = 0.20, dry = 0.82, room = 0.55, damp = 0.50},
      },
    },
  },
  ["lead-back"] = {
    volumes = {
      ["AI Lead Player"] = 0.095,
      ["AI Guitar Player"] = 0.14,
      ["AI Keyboard Player"] = 0.070,
    },
    effects = {
      ["AI Lead Player"] = {
        ["ReaVerbate"] = {wet = 0.19, dry = 0.80, room = 0.50, damp = 0.54},
      },
    },
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

function M.normalize_mix_profile(profile)
  local normalized = (profile or ""):lower():gsub("^%s+", ""):gsub("%s+$", ""):gsub("%s+", "-")
  if normalized == "" or normalized == "default" or normalized == "1" then
    return "balanced"
  end
  if normalized == "2" or normalized == "drums" then
    return "drums-forward"
  end
  if normalized == "3" or normalized == "warm" or normalized == "room" then
    return "warmer-room"
  end
  if normalized == "4" or normalized == "lead" then
    return "lead-back"
  end
  if M.MIX_PROFILES[normalized] then
    return normalized
  end
  return "balanced"
end

function M.apply_mix_profile(profile)
  local normalized = M.normalize_mix_profile(profile)
  local profile_settings = M.MIX_PROFILES[normalized]
  if not profile_settings then
    return normalized
  end

  for track_name_value, volume in pairs(profile_settings.volumes or {}) do
    M.TRACK_VOLUMES[track_name_value] = volume
  end

  for track_name_value, effects in pairs(profile_settings.effects or {}) do
    M.EFFECT_PARAM_TARGETS[track_name_value] = M.EFFECT_PARAM_TARGETS[track_name_value] or {}
    for effect_name, params in pairs(effects) do
      M.EFFECT_PARAM_TARGETS[track_name_value][effect_name] = M.EFFECT_PARAM_TARGETS[track_name_value][effect_name] or {}
      for param_name, value in pairs(params) do
        M.EFFECT_PARAM_TARGETS[track_name_value][effect_name][param_name] = value
      end
    end
  end

  return normalized
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
          M.set_effect_params(track, fx_index, name, effect.needle)
          configured = configured + 1
          if was_added then added = added + 1 end
        end
      end
    end
  end

  return configured, added
end

function M.set_effect_params(track, fx_index, track_name_value, effect_needle)
  local track_settings = M.EFFECT_PARAM_TARGETS[track_name_value]
  if not track_settings then return end
  local targets = track_settings[effect_needle]
  if not targets then return end

  if targets.wet ~= nil then
    M.set_param_by_name(track, fx_index, {"wet"}, targets.wet)
  end
  if targets.dry ~= nil then
    M.set_param_by_name(track, fx_index, {"dry"}, targets.dry)
  end
  if targets.room ~= nil then
    M.set_param_by_name(track, fx_index, {"room", "size"}, targets.room)
  end
  if targets.damp ~= nil then
    M.set_param_by_name(track, fx_index, {"damp"}, targets.damp)
  end
end

function M.set_param_by_name(track, fx_index, needles, value)
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

return M
