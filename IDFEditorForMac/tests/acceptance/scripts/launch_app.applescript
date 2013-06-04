tell application "/Users/patrick/Development/Projects/EnergyPlusToolsForMac/IDFEditorForMac/build/Release/IDFEditorForMac.app" to activate

tell application "System Events"
	tell process "IDFEditorForMac"
		set frontmost to true
		perform action "AXRaise" of (windows whose title is "IDFEditorForMac")
	end tell
end tell
