-- A single native HTTP request feeds every bar and desktop instance.
local HOUR = 3600000
local URL = "https://api.open-meteo.com/v1/forecast?latitude=-26.3375&longitude=-49.9061&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=America%2FSao_Paulo&forecast_days=1"
local pending = false
local dir = noctalia.pluginDataDir()
local cachePath = dir and (dir .. "/weather.json") or nil
local data = nil

local function valid(value)
    return type(value) == "table" and type(value.current) == "table"
        and type(value.current.temperature_2m) == "number"
        and type(value.current.weather_code) == "number"
        and type(value.fetchedAt) == "number"
end

local function publish(stale)
    noctalia.state.set("weather", { data = data, stale = stale })
end

local function failed()
    pending = false
    publish(true)
    noctalia.log("Não foi possível atualizar a meteorologia; mantendo o cache.")
end

local function refresh()
    if pending then return end
    pending = true
    local accepted = noctalia.http({ url = URL }, function(response)
        pending = false
        if not response.ok or response.status ~= 200 then failed(); return end
        local decoded = noctalia.json.decode(response.body)
        if type(decoded) ~= "table" then failed(); return end
        decoded.fetchedAt = noctalia.nowMs()
        if not valid(decoded) then failed(); return end
        data = decoded
        publish(false)
        if cachePath then
            local encoded = noctalia.json.encode(data)
            if encoded then noctalia.writeFile(cachePath, encoded) end
        end
    end)
    if not accepted then failed() end
end

if cachePath and noctalia.fileExists(cachePath) then
    local raw = noctalia.readFile(cachePath)
    if raw then
        local cached = noctalia.json.decode(raw)
        if valid(cached) then data = cached end
    end
end

function update()
    refresh()
end

-- No per-second/frame updates; preserve the cache age across shell restarts.
noctalia.setUpdateInterval(HOUR)
publish(not data or noctalia.nowMs() < data.fetchedAt or noctalia.nowMs() - data.fetchedAt >= HOUR)
-- Align the first tick with the cached response's expiry.
if data and noctalia.nowMs() >= data.fetchedAt and noctalia.nowMs() - data.fetchedAt < HOUR then
    noctalia.setUpdateInterval(math.max(1000, HOUR - (noctalia.nowMs() - data.fetchedAt)))
    local initialUpdate = update
    function update()
        noctalia.setUpdateInterval(HOUR)
        initialUpdate()
    end
else
    refresh()
end
