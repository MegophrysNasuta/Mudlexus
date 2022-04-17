const lua = {};
const LuaVM = require('lua.vm.js');
const L = new LuaVM.Lua.State();

lua.execute = (code) => {
  L.load(code).invoke(Array.prototype.slice.call(arguments, 1))
}

lua.execute(`
-- table, (c|d|h)echo
send_command = js.global.send_command
display_notice = js.global.display_notice
reflex_enable = js.global.reflex_enable
reflex_disable = js.global.reflex_disable

--https://wiki.mudlet.org/w/Manual:Basic_Essentials#send

--Mudlet: send(command, showOnScreen)
--Nexus: send_command(input, noExpansion)

--noExpansion is more like send vs expandAlias
--no on-demand equivalent to showOnScreen in Nexus
function send(command, showOnScreen)
  send_command(command, true)
end

--https://wiki.mudlet.org/w/Manual:Lua_Functions#sendAll

--Mudlet: sendAll(list of things to send, echoBackOrNot)
--Nexus: send_command(input, noExpansion) (in a loop basically)

--noExpansion is more like send vs expandAlias
--no on-demand equivalent of echoBackOrNot in Nexus
function sendAll(args)
  local length = #args
  local lastArg = args[length]
  if not lastArg then length = length - 1 end

  for i, arg in pairs(args) do
    if i <= length then
      send_command(arg, true)
    end
  end
end

--https://wiki.mudlet.org/w/Manual:Miscellaneous_Functions#expandAlias

--Mudlet: expandAlias(command, echoBackToBuffer)
--Nexus: send_command(input, noExpansion)

--noExpansion is more like send vs expandAlias
--no on-demand equivalent to echoBackToBuffer in Nexus
function expandAlias(command, echoBackToBuffer)
  send_command(command, false)
end

--https://wiki.mudlet.org/w/Manual:Basic_Essentials#echo

--Mudlet: echo([miniconsoleName or labelName], text)
--Nexus: display_notice(text, fgcolor, bgcolor)

--miniconsole/label support is beyond the scope of this project
function echo(maybeText, maybeAlsoText)
  local text
  if not maybeAlsoText then text = maybeText else text = maybeAlsoText end
  display_notice(text)
end

--https://wiki.mudlet.org/w/Manual:Mudlet_Object_Functions#enableAlias
--https://wiki.mudlet.org/w/Manual:Mudlet_Object_Functions#enableKey
--https://wiki.mudlet.org/w/Manual:Mudlet_Object_Functions#enableTrigger

--https://wiki.mudlet.org/w/Manual:Mudlet_Object_Functions#disableAlias
--https://wiki.mudlet.org/w/Manual:Mudlet_Object_Functions#disableKey
--https://wiki.mudlet.org/w/Manual:Mudlet_Object_Functions#disableTrigger

--Example
--=======
--Mudlet: enableAlias(name)
--Nexus: reflex_enable(reflex_find_by_name('alias',
--                                         name,
--                                         // should search be case sensitive?
--                                         false,
--                                         // should we ignore disabled results?
--                                         false)
function enableAlias(name)
  reflex_enable(reflex_find_by_name('alias', name, false, false))
end
function disableAlias(name)
  reflex_disable(reflex_find_by_name('alias', name, false, true))
end
function enableKey(name)
  reflex_enable(reflex_find_by_name('keybind', name, false, false))
end
function disableKey(name)
  reflex_disable(reflex_find_by_name('keybind', name, false, true))
end
function enableTrigger(name)
  reflex_enable(reflex_find_by_name('trigger', name, false, false))
end
function disableTrigger(name)
  reflex_disable(reflex_find_by_name('trigger', name, false, true))
end
`)
