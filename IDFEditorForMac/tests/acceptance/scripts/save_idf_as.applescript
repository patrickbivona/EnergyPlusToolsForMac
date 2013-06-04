on run argv
	set dest_dir to item 1 of argv
	set dest_file_basename to item 2 of argv
	
	tell application "System Events"
		tell process "IDFEditorForMac"
			-- alternative: keystroke "s" using {command down, option down, shift down}
			key down {option}
			click menu item "Save As…" of menu "File" of menu bar 1
			key up {option}
			
			keystroke "g" using {command down, shift down}
			set value of attribute "AXValue" of text field 1 of sheet 1 of sheet 1 of front window to dest_dir
			keystroke return
			delay 0.5
			
			keystroke dest_file_basename
			delay 0.5
			keystroke return
		end tell
	end tell
	
end run