-- AI Band: import a generated MIDI sketch into the current REAPER project.

local ok, file = reaper.GetUserFileNameForRead("", "Import AI Band MIDI", ".mid")
if not ok then
  return
end

reaper.Undo_BeginBlock()
reaper.InsertMedia(file, 0)
reaper.Undo_EndBlock("Import AI Band MIDI", -1)

