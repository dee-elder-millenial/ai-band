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
  .. "  \"project_path\": \"" .. escape_json(project_path or "") .. "\"\n"
  .. "}\n"

local file = io.open(DEFAULT_CUE, "w")
if not file then
  reaper.ShowMessageBox("Could not write cue file:\n" .. DEFAULT_CUE, "AI Band", 0)
  return
end

file:write(json)
file:close()

reaper.ShowMessageBox("Wrote AI Band cue:\n" .. instruction, "AI Band", 0)

