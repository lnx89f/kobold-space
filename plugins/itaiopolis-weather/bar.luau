local function number(value, unit)
    if type(value) ~= "number" then return "—" end
    return string.format("%.0f", value) .. unit
end

local function render(state)
    local data = state and state.data
    if not data then
        barWidget.setGlyph("cloud")
        barWidget.setText("—°C")
        barWidget.setTooltip("Itaiópolis · SC\nAguardando conexão para carregar o clima.")
        return
    end
    local current = data.current
    local code = current.weather_code
    local glyph = "cloud"
    local condition = "Nublado"
    if code == 0 then glyph = current.is_day == 0 and "moon" or "sun"; condition = "Céu limpo"
    elseif code <= 2 then glyph = "cloud-sun"; condition = "Parcialmente nublado"
    elseif code == 45 or code == 48 then glyph = "mist"; condition = "Nevoeiro"
    elseif code >= 95 then glyph = "cloud-storm"; condition = "Trovoadas"
    elseif code == 71 or code == 73 or code == 75 or code == 77 or code == 85 or code == 86 then glyph = "cloud-snow"; condition = "Neve"
    elseif code >= 51 then glyph = "cloud-rain"; condition = "Chuva" end
    barWidget.setGlyph(glyph)
    barWidget.setText(number(current.temperature_2m, "°C") .. (state.stale and " *" or ""))
    local daily = data.daily or {}
    barWidget.setTooltip("Itaiópolis · SC\n" .. condition
        .. "\nSensação: " .. number(current.apparent_temperature, "°C")
        .. "\nMín./máx.: " .. number(daily.temperature_2m_min and daily.temperature_2m_min[1], "°C") .. " / " .. number(daily.temperature_2m_max and daily.temperature_2m_max[1], "°C")
        .. "\nUmidade: " .. number(current.relative_humidity_2m, "%")
        .. " · Vento: " .. number(current.wind_speed_10m, " km/h")
        .. "\nAtualizado: " .. noctalia.formatTime("{:%d/%m %H:%M}", data.fetchedAt / 1000, "America/Sao_Paulo")
        .. (state.stale and "\nSem conexão · últimos dados disponíveis" or "")
        .. "\nFonte: Open-Meteo · atualização a cada hora")
end

noctalia.setUpdateInterval(3600000)
function update() render(noctalia.state.get("weather")) end
noctalia.state.watch("weather", render)
update()
