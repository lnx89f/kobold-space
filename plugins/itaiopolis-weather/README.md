# Clima de Itaiópolis

Plugin local para Noctalia 5, habilitado como `kobold/itaiopolis-weather`.

## Adicionar pela interface

- Barra: Configurações → Barra → adicionar widget → Clima de Itaiópolis (`kobold/itaiopolis-weather:bar`).
- Desktop: Configurações → Widgets do desktop → adicionar → Clima de Itaiópolis (`kobold/itaiopolis-weather:desktop`). Ative os widgets do desktop e posicione o cartão no editor.
- As apresentações são opcionais: habilitar o plugin disponibiliza as entradas, sem adicioná-las automaticamente ao layout.
- Para suspender também as consultas, desative o plugin em Configurações → Plugins.

O Noctalia carrega o registro na próxima inicialização. Com ele em execução, use `noctalia msg config-reload` para recarregar alterações na configuração.

## Funcionamento

Um serviço compartilhado consulta o Open-Meteo a cada 3.600.000 ms (uma hora), usando o cliente HTTP nativo do Noctalia, sem processos externos e sem chave de API. A barra mostra temperatura e ícone, com detalhes ao passar o mouse. O desktop mostra condição, sensação térmica, mínima/máxima, umidade, vento e probabilidade de chuva do dia.

Localização fixa: Itaiópolis/SC, latitude -26.3375, longitude -49.9061, fuso America/Sao_Paulo. Unidades: °C, km/h e %.

Os dados ficam no diretório persistente do plugin, em `weather.json`. Reiniciar o shell reutiliza o cache e respeita seu prazo de uma hora. Em falhas de rede, mantém os últimos dados e indica que estão desatualizados; a próxima tentativa ocorre no ciclo seguinte. Sem cache, exibe um estado de espera. O modo offline do Noctalia é respeitado pelo cliente HTTP nativo.

Fonte: https://open-meteo.com/en/docs
Coordenadas: https://turismo.itaiopolis.sc.gov.br/pagina-154/

## Verificação

`noctalia plugins lint ~/.local/share/noctalia/plugins/itaiopolis-weather`

Manifesto/configuração validados. Lógica de consulta, cache, falhas e renderização verificada com um host Lua simulado. A apresentação visual e a consulta real dependem do Noctalia em execução e de acesso à internet.
