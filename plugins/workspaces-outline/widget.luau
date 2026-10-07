local workspaces = {}
local pending = false
local refreshAgain = false

local function render()
    local children = {}
    local output = barWidget.outputName()
    table.sort(workspaces, function(a, b) return a.idx < b.idx end)
    for _, workspace in ipairs(workspaces) do
        if output == nil or workspace.output == output then
            local color = "outline"
            if workspace.is_urgent then
                color = "secondary"
            elseif workspace.is_active then
                color = "primary"
            elseif workspace.active_window_id ~= nil then
                color = "secondary/0.65"
            end
            local index = workspace.idx
            table.insert(children, ui.column({
                key = tostring(workspace.id),
                width = 18,
                height = 18,
                align = "center",
                justify = "center",
                fill = "#00000000",
                border = color,
                borderWidth = 1,
                radius = 9,
                onClick = function()
                    noctalia.runAsync({ "niri", "msg", "action", "focus-workspace", tostring(index) })
                end,
            }, {
                ui.label({
                    text = tostring(index),
                    fontSize = 11,
                    color = color,
                    baseline = "inkCentered",
                    textAlign = "center",
                }),
            }))
        end
    end
    local container = barWidget.isVertical() and ui.column or ui.row
    barWidget.render(container({ gap = 4, align = "center", fill = "#00000000" }, children))
end

local refresh
refresh = function()
    if pending then
        refreshAgain = true
        return
    end
    pending = true
    local accepted = noctalia.runAsync({ "niri", "msg", "-j", "workspaces" }, function(result)
        pending = false
        if result.exitCode == 0 then
            local decoded = noctalia.json.decode(result.stdout)
            if type(decoded) == "table" then
                workspaces = decoded
                render()
            end
        end
        if refreshAgain then
            refreshAgain = false
            refresh()
        end
    end)
    if not accepted then pending = false end
end

function update()
    refresh()
end

function onScroll(axis, steps, startsGesture)
    if axis == "vertical" and startsGesture then
        noctalia.runAsync({ "niri", "msg", "action", steps > 0 and "focus-workspace-down" or "focus-workspace-up" })
    end
end

noctalia.setUpdateInterval(5000)
noctalia.runStream("niri msg -j event-stream", function(line)
    if string.find(line, '"Workspace', 1, true) then
        refresh()
    end
end)
refresh()
