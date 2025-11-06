# 🔍 DOMAIN FINDER

Buscador paralelo de dominios disponible con soporte para múltiples TLDs y longitudes.

![ASCII Banner](https://img.shields.io/badge/DOMAIN-FINDER-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.6+-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

# CARACTERÍSTICAS

- ⚡ **Procesamiento paralelo ultra-rápido** con múltiples estrategias
- 🌍 **50+ TLDs soportados** organizados por categorías
- 📏 **Soporte para 3 y 4 letras** (17,576 - 456,976 combinaciones)
- 🎯 **Benchmark automático** para encontrar la mejor estrategia
- 📊 **Estadísticas en tiempo real** y progreso detallado
- 💾 **Resultados guardados** en archivos organizados

# INSTALACIÓN

```bash
# Clonar o descargar los archivos
chmod +x start.sh
./start.sh

# O ejecutar directamente
chmod +x domain_finder.py
python3 domain_finder.py
```

# DEPENDENCIAS

```bash
pip install -r requirements.txt
```

# TLDS SOPORTADOS

## 🌟 POPULARES
| TLD | Descripción | Uso |
|-----|-------------|-----|
| `.com` | Comercial | Más popular |
| `.net` | Red | Infraestructura |
| `.org` | Organización | Sin fines de lucro |
| `.io` | Tecnología | Startups |
| `.co` | Compañía | Alternativa .com |
| `.me` | Personal | Blogs, portfolios |
| `.tv` | Televisión | Contenido multimedia |
| `.cc` | Islas Cocos | General |
| `.ws` | Samoa | Sitios web |
| `.info` | Información | Contenido informativo |

## 🏢 GENÉRICOS (GTLD)
| TLD | Descripción | Restricciones |
|-----|-------------|---------------|
| `.biz` | Negocios | Verificación requerida |
| `.name` | Nombre personal | Individuos |
| `.pro` | Profesional | Licencia requerida |
| `.travel` | Viajes | Industria turística |
| `.museum` | Museos | Instituciones culturales |
| `.aero` | Aviación | Industria aeronáutica |
| `.coop` | Cooperativas | Organizaciones cooperativas |

## 🌍 AMÉRICA
| TLD | País | Popularidad |
|-----|------|-------------|
| `.us` | Estados Unidos | 🇺🇸 Alto |
| `.ca` | Canadá | 🇨🇦 Alto |
| `.mx` | México | 🇲🇽 Alto |
| `.ar` | Argentina | 🇦🇷 Medio |
| `.cl` | Chile | 🇨🇱 Medio |
| `.pe` | Perú | 🇵🇪 Medio |
| `.co` | Colombia | 🇨🇴 Alto |
| `.ve` | Venezuela | 🇻🇪 Bajo |
| `.ec` | Ecuador | 🇪🇨 Bajo |
| `.uy` | Uruguay | 🇺🇾 Bajo |

## 🇪🇺 EUROPA
| TLD | País | Popularidad |
|-----|------|-------------|
| `.uk` | Reino Unido | 🇬🇧 Alto |
| `.de` | Alemania | 🇩🇪 Alto |
| `.fr` | Francia | 🇫🇷 Alto |
| `.it` | Italia | 🇮🇹 Medio |
| `.es` | España | 🇪🇸 Alto |
| `.nl` | Países Bajos | 🇳🇱 Alto |
| `.be` | Bélgica | 🇧🇪 Medio |
| `.at` | Austria | 🇦🇹 Medio |
| `.ch` | Suiza | 🇨🇭 Alto |
| `.se` | Suecia | 🇸🇪 Medio |

## 🌏 ASIA
| TLD | País | Popularidad |
|-----|------|-------------|
| `.jp` | Japón | 🇯🇵 Alto |
| `.cn` | China | 🇨🇳 Alto |
| `.kr` | Corea del Sur | 🇰🇷 Alto |
| `.in` | India | 🇮🇳 Alto |
| `.sg` | Singapur | 🇸🇬 Alto |
| `.hk` | Hong Kong | 🇭🇰 Medio |
| `.tw` | Taiwán | 🇹🇼 Medio |
| `.th` | Tailandia | 🇹🇭 Medio |
| `.ph` | Filipinas | 🇵🇭 Medio |
| `.my` | Malasia | 🇲🇾 Medio |

## 🏛️ GUBERNAMENTALES
| TLD | Uso | Restricciones |
|-----|-----|---------------|
| `.gov` | Gobierno EE.UU. | Agencias gubernamentales |
| `.edu` | Educación | Instituciones acreditadas |
| `.mil` | Militar | Fuerzas armadas EE.UU. |

# PROCESAMIENTO PARALELO

## ESTRATEGIAS DISPONIBLES

| Estrategia | Dominios/Lote | Workers | Velocidad | Uso CPU | Estabilidad |
|------------|---------------|---------|-----------|---------|------------|
| ⚡ Rápida | 1 | 100 | Máxima | Alto | Media |
| 🎯 Balanceada | 10 | 30 | Alta | Medio | Alta |
| 🐢 Estable | 50 | 10 | Media | Bajo | Máxima |
| 🔧 Personalizada | Variable | Variable | Variable | Variable | Variable |

## ¿CÓMO FUNCIONA EL BENCHMARK?

1. **Genera muestra**: 1,000 dominios aleatorios
2. **Prueba cada estrategia**: Mide tiempo real
3. **Calcula métricas**: Velocidad (dom/s), éxito, estabilidad
4. **Selecciona óptima**: Basada en menor tiempo total

## ALGORITMO DE PROCESAMIENTO

```python
# 1. Generar combinaciones
domains = generate_domains(length, tld)  # 26^length combinaciones

# 2. Dividir en lotes
batches = create_batches(domains, batch_size)

# 3. Procesamiento paralelo
with ThreadPoolExecutor(max_workers=workers) as executor:
    futures = [executor.submit(check_domain_batch, batch) for batch in batches]
    
# 4. Recopilar resultados
for future in as_completed(futures):
    results = future.result()
    available.extend([d for d, available in results if available])
```

## FLUJO DE VERIFICACIÓN

1. **RDAP Query**: `GET https://rdap.org/domain/{domain}`
2. **Response Analysis**:
   - `404` = Dominio disponible ✅
   - `200` = Dominio registrado ❌
   - `Otro` = Error, asumir registrado ❌

## OPTIMIZACIONES IMPLEMENTADAS

- ✅ **Connection Pooling**: Reutiliza conexiones HTTP
- ✅ **Timeout Management**: 2 segundos por petición
- ✅ **Batch Processing**: Reduce overhead de threads
- ✅ **Progress Tracking**: Actualización cada 500 dominios
- ✅ **Memory Efficient**: Procesamiento streaming

# USO INTERACTIVO

## MENÚ PRINCIPAL

```
============================================================
                     🔍 DOMAIN FINDER 🔍
                Buscador de Dominios Disponibles
============================================================
```

## OPCIONES DE CONFIGURACIÓN

1. **Seleccionar TLD**: Menú numérico con 50+ opciones en 3 columnas
2. **Longitud**: 3 letras (17,576) o 4 letras (456,976)
3. **Estrategia**: Automática, rápida, balanceada, estable o personalizada

## SELECCIÓN MÚLTIPLE DE TLDS

Puedes seleccionar:
- **Individual**: `5` (solo .io)
- **Múltiple**: `1,3,5` (.com, .org, .io)
- **Rango**: `1-5` (.com, .net, .org, .io, .co)
- **Mixto**: `1-3,8,10` (.com, .net, .org, .me, .info)
- **Todos**: `todos` (los 50 TLDs)

# ARCHIVOS DE SALIDA

Los resultados se guardan con formato:
```
dominios_disponibles_{longitud}letras_{tlds}.txt
```

Ejemplos:
- `dominios_disponibles_3letras_com.txt`
- `dominios_disponibles_4letras_io.txt`
- `dominios_disponibles_3letras_com_io_me.txt`

# MÉTRICAS Y ESTADÍSTICAS

## DURANTE LA BÚSQUEDA
- 📈 Progreso: `1,000/17,576 (5.7%)`
- ⚡ Velocidad: `150.2 dom/s`
- ⏱️ ETA: `110.5s`

## RESULTADOS FINALES
- ✅ Tiempo total: `120.3 segundos`
- 🎯 Dominios disponibles: `23`
- 📈 Eficiencia: `0.131% disponibles`
- ⚡ Velocidad promedio: `146.1 dominios/segundo`

# ARQUITECTURA TÉCNICA

## COMPONENTES PRINCIPALES

1. **Domain Generator**: Crea combinaciones alfabéticas
2. **RDAP Client**: Verifica disponibilidad via HTTP
3. **Batch Processor**: Agrupa dominios para eficiencia
4. **Parallel Executor**: Gestiona threads concurrentes
5. **Result Collector**: Agrega dominios disponibles

## TECNOLOGÍAS UTILIZADAS

- **Python 3.6+**: Lenguaje principal
- **ThreadPoolExecutor**: Paralelismo integrado
- **Requests**: Cliente HTTP
- **RDAP Protocol**: WHOIS moderno

# RENDIMIENTO

## BENCHMARKS TÍPICOS

| Búsqueda | Dominios | Tiempo | Velocidad | Encontrados |
|----------|----------|--------|-----------|-------------|
| 3 letras .com | 17,576 | 120s | 146 dom/s | 15-25 |
| 4 letras .com | 456,976 | 3,200s | 143 dom/s | 200-400 |
| 3 letras .io | 17,576 | 115s | 153 dom/s | 8-15 |
| 3 letras .es | 17,576 | 125s | 141 dom/s | 20-35 |

## FACTORES QUE AFECTAN EL RENDIMIENTO

- 🌐 **Velocidad de Internet**: Latencia a servidores RDAP
- 💻 **CPU**: Número de cores para threads
- 🔄 **Concurrency**: Workers vs batch size óptimo
- 📍 **Geografía**: Distancia a servidores RDAP

# PERSONALIZACIÓN

## MODIFICAR ESTRATEGIAS

```python
# En domain_finder.py, modificar la lista strategies:
strategies = [
    (1, 100),   # batch_size, max_workers
    (4, 75),    # Nueva estrategia añadida
    (10, 30),
    (20, 20),
    (50, 10),
]
```

## AGREGAR NUEVOS TLDS

```python
def get_all_tlds():
    return {
        "🆕 NUEVOS": [
            ".xyz", ".app", ".dev", ".tech", ".ai"
        ],
        # ... categorías existentes
    }
```

# LIMITACIONES

- ⚠️ **Rate Limiting**: Algunos TLDs pueden limitar peticiones
- 🌐 **Dependencia de Red**: Requiere conexión estable
- 💾 **Memoria**: 4 letras usa ~50MB RAM
- ⏱️ **Tiempo**: Búsquedas largas pueden tardar horas

# LICENCIA

MIT License - Libre para uso comercial y personal.

# CONTRIBUCIONES

¡Contribuciones bienvenidas! 
- Reportar bugs en Issues
- Sugerir nuevos TLDs
- Mejorar algoritmos de paralelización

---

**🚀 DOMAIN FINDER - Encuentra tu dominio perfecto!**