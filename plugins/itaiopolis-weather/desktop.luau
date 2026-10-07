local function number(value, unit)
    if type(value) ~= "number" then return "—" end
    return string.format("%.0f", value) .. unit
end

local function render(state)
    local data = state and state.data
    local current = data and data.current or {}
    local daily = data and data.daily or {}
    local code = current.weather_code
    local glyph, condition = "cloud", "Aguardando conexão…"
    if code then
        condition = "Nublado"
        if code == 0 then glyph = current.is_day == 0 and "moon" or "sun"; condition = "Céu limpo"
        elseif code <= 2 then glyph = "cloud-sun"; condition = "Parcialmente nublado"
        elseif code == 45 or code == 48 then glyph = "mist"; condition = "Nevoeiro"
        elseif code >= 95 then glyph = "cloud-storm"; condition = "Trovoadas"
        elseif code == 71 or code == 73 or code == 75 or code == 77 or code == 85 or code == 86 then glyph = "cloud-snow"; condition = "Neve"
        elseif code >= 51 then glyph = "cloud-rain"; condition = "Chuva" end
    end
    desktopWidget.render(ui.column({ padding = 16, gap = 8, minWidth = 250,
        fill = "surface/0.85", border = "outline/0.3", borderWidth = 1, radius = 16 }, {
        ui.label({ text = "Itaiópolis · SC", fontSize = 15, fontWeight = "bold" }),
        ui.row({ gap = 12, align = "center" }, {
            ui.glyph({ name = glyph, size = 34, color = "primary" }),
            ui.label({ text = number(current.temperature_2m, "°C"), fontSize = 32, fontWeight = "bold" }),
        }),
        ui.label({ text = condition, fontSize = 13 }),
        ui.label({ text = "Sensação " .. number(current.apparent_temperature, "°C"), fontSize = 12, color = "on_surface/0.7" }),
        ui.label({ text = "↓ " .. number(daily.temperature_2m_min and daily.temperature_2m_min[1], "°C") .. "    ↑ " .. number(daily.temperature_2m_max and daily.temperature_2m_max[1], "°C"), fontSize = 13 }),
        ui.label({ text = "Umidade " .. number(current.relative_humidity_2m, "%") .. " · Vento " .. number(current.wind_speed_10m, " km/h"), fontSize = 12 }),
        ui.label({ text = "Chance de chuva hoje: " .. number(daily.precipitation_probability_max and daily.precipitation_probability_max[1], "%"), fontSize = 12 }),
        ui.label({ text = data and ("Atualizado " .. noctalia.formatTime("{:%d/%m %H:%M}", data.fetchedAt / 1000, "America/Sao_Paulo")) or "Atualização a cada hora", fontSize = 10, color = "on_surface/0.6" }),
        ui.label({ text = data and state and state.stale and "Sem conexão · últimos dados disponíveis" or "Open-Meteo · atualização a cada hora", fontSize = 10, color = "on_surface/0.6" }),
    }))
end

noctalia.setUpdateInterval(3600000)
function update() render(noctalia.state.get("weather")) end
noctalia.state.watch("weather", render)
update()
