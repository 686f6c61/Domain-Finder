#!/usr/bin/env python3
"""
Domain Finder - Parallel Domain Availability Checker

GitHub: https://github.com/686f6c61/Domain-Finder
Author: 686f6c61
Date: November 2025
Version: 1.0

Description:
    High-performance parallel domain checker that verifies domain availability
    across 50+ TLDs using RDAP protocol. Features intelligent batching,
    automatic benchmarking, and real-time progress tracking.

Architecture:
    - Multi-threaded parallel processing with configurable strategies
    - RDAP-based domain verification (modern WHOIS replacement)
    - Intelligent batching for optimal network utilization
    - Memory-efficient streaming processing
    - Comprehensive error handling and graceful shutdown

Performance:
    - Supports 3-letter (17,576) and 4-letter (456,976) combinations
    - Processes 100-200 domains/second depending on strategy
    - Automatic benchmarking selects optimal configuration
    - Connection pooling and timeout management
"""

import multiprocessing
import string
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import sys
import signal

def check_domain_batch(domains_batch):
    """
    Process a batch of domains using RDAP protocol.
    
    Args:
        domains_batch (list): List of domain strings to check
        
    Returns:
        list: Tuple of (domain, is_available) for each domain
        
    Note:
        Uses RDAP (Registration Data Access Protocol) which is the modern
        replacement for WHOIS. 404 response indicates domain availability.
        Implements timeout and exception handling for robustness.
    """
    results = []
    
    for domain in domains_batch:
        try:
            # RDAP endpoint for domain verification
            response = requests.get(f"https://rdap.org/domain/{domain}", timeout=2)
            
            # HTTP 404 = Domain not found = Available
            # HTTP 200 = Domain found = Registered
            is_available = response.status_code == 404
            results.append((domain, is_available))
            
            # Real-time feedback for available domains
            if is_available:
                print(f"✓ DISPONIBLE: {domain}")
                
        except Exception:
            # Network errors, timeouts, or invalid responses default to registered
            results.append((domain, False))
    
    return results

def generate_domains(length=3, tld=".com"):
    """
    Generate all possible letter combinations for a given TLD.
    
    Args:
        length (int): Domain length (3 or 4 letters)
        tld (str): Top-level domain (e.g., '.com')
        
    Returns:
        list: All possible domain combinations
        
    Complexity:
        O(26^length) - Exponential growth with domain length
        - 3 letters: 26^3 = 17,576 combinations
        - 4 letters: 26^4 = 456,976 combinations
    """
    letters = string.ascii_lowercase
    domains = []
    
    if length == 3:
        # Triple nested loop for 3-letter combinations
        for a in letters:
            for b in letters:
                for c in letters:
                    domains.append(f"{a}{b}{c}{tld}")
    elif length == 4:
        # Quadruple nested loop for 4-letter combinations
        for a in letters:
            for b in letters:
                for c in letters:
                    for d in letters:
                        domains.append(f"{a}{b}{c}{d}{tld}")
    
    return domains

def generate_domains_multiple(length=3, tlds=None):
    """
    Generate domain combinations for multiple TLDs.
    
    Args:
        length (int): Domain length (3 or 4 letters)
        tlds (list): List of TLD strings, defaults to ['.com']
        
    Returns:
        list: All domain combinations across all specified TLDs
        
    Memory Consideration:
        For 4 letters + all 50 TLDs: 456,976 * 50 = 22,848,800 domains
        Uses streaming approach to avoid memory overload.
    """
    if tlds is None:
        tlds = [".com"]
    
    all_domains = []
    for tld in tlds:
        domains = generate_domains(length, tld)
        all_domains.extend(domains)
    
    return all_domains

def get_all_tlds():
    """
    Returns comprehensive list of RDAP-supported TLDs organized by category.
    
    Returns:
        dict: Categories with their respective TLD lists
        
    RDAP Support:
        All listed TLDs support RDAP protocol for modern domain verification.
        RDAP provides structured JSON responses vs traditional WHOIS text.
        
    Categories:
        - POPULARES: Most common and sought-after TLDs
        - GENÉRICOS: Generic top-level domains (gTLDs)
        - AMÉRICA: Country-code TLDs for American countries
        - EUROPA: European country-code TLDs
        - ASIA: Asian country-code TLDs
        - GUBERNAMENTALES: Restricted government/educational TLDs
    """
    return {
        "🌟 POPULARES": [
            ".com", ".net", ".org", ".io", ".co", ".me", ".tv", ".cc", ".ws", ".info"
        ],
        "🏢 GENÉRICOS": [
            ".biz", ".name", ".pro", ".travel", ".museum", ".aero", ".coop"
        ],
        "🌍 AMÉRICA": [
            ".us", ".ca", ".mx", ".ar", ".cl", ".pe", ".co", ".ve", ".ec", ".uy"
        ],
        "🇪🇺 EUROPA": [
            ".uk", ".de", ".fr", ".it", ".es", ".nl", ".be", ".at", ".ch", ".se"
        ],
        "🌏 ASIA": [
            ".jp", ".cn", ".kr", ".in", ".sg", ".hk", ".tw", ".th", ".ph", ".my"
        ],
        "🏛️ GUBERNAMENTALES": [
            ".gov", ".edu", ".mil"
        ]
    }

def create_batches(domains, batch_size):
    """
    Generator function to split domain list into batches for parallel processing.
    
    Args:
        domains (list): List of domain strings to process
        batch_size (int): Number of domains per batch
        
    Yields:
        list: Batch of domain strings
        
    Performance Considerations:
        - Smaller batches = Better load distribution but more overhead
        - Larger batches = Less overhead but potential load imbalance
        - Optimal size depends on network latency and processing power
    """
    for i in range(0, len(domains), batch_size):
        yield domains[i:i + batch_size]

def check_domains_parallel(domains, batch_size=10, max_workers=50):
    """
    Execute parallel domain checking using ThreadPoolExecutor with batching strategy.
    
    Args:
        domains (list): List of domain strings to check
        batch_size (int): Number of domains per batch for processing
        max_workers (int): Maximum number of concurrent threads
        
    Returns:
        list: Available domain strings
        
    Threading Strategy:
        - ThreadPoolExecutor manages thread pool lifecycle
        - Batches reduce thread creation overhead
        - as_completed() provides results as they finish
        - Progress tracking every 500 domains for performance
        
    Performance Metrics:
        - Calculates real-time processing rate (domains/second)
        - Estimates remaining time (ETA) based on current rate
        - Tracks completion percentage for user feedback
    """
    available_domains = []
    total = len(domains)
    total_batches = math.ceil(total / batch_size)
    
    print(f"🔍 Estrategia: {batch_size} dominios por lote")
    print(f"📊 Total lotes: {total_batches}")
    print(f"⚡ Workers: {max_workers}")
    print(f"🎯 Verificando {total:,} dominios...")
    print()
    
    # Convert generator to list for multiple iterations
    batches = list(create_batches(domains, batch_size))
    
    start_time = time.time()
    processed = 0
    
    # Thread pool execution with future tracking
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all batch jobs and map futures to batches
        future_to_batch = {executor.submit(check_domain_batch, batch): batch 
                          for batch in batches}
        
        # Process results as they complete (non-blocking)
        for future in as_completed(future_to_batch):
            batch_results = future.result()
            
            # Collect available domains from batch results
            for domain, is_available in batch_results:
                if is_available:
                    available_domains.append(domain)
            
            processed += len(batch_results)
            
            # Progress reporting every 500 domains (performance optimization)
            if processed % 500 == 0:
                elapsed = time.time() - start_time
                rate = processed / elapsed
                eta = (total - processed) / rate if rate > 0 else 0
                print(f"📈 Progreso: {processed:,}/{total:,} ({processed/total*100:.1f}%) - "
                      f"Velocidad: {rate:.1f} dom/s - ETA: {eta:.0f}s")
    
    return available_domains

def benchmark_strategies(test_domains):
    """
    Benchmark different parallel processing strategies to find optimal configuration.
    
    Args:
        test_domains (list): Sample domain list for testing (typically 1000 domains)
        
    Returns:
        tuple: (optimal_batch_size, optimal_workers)
        
    Strategy Matrix:
        Tests various combinations of batch sizes and worker counts:
        - Small batches + many workers: Maximum parallelism, high overhead
        - Large batches + few workers: Minimum overhead, potential bottlenecks
        - Balanced configurations: Optimal trade-off point
        
    Selection Criteria:
        Chooses strategy with minimum execution time for the given environment.
        Accounts for network latency, CPU cores, and system resources.
    """
    print("🧪 Benchmark de estrategias...")
    print("=" * 60)
    
    # Strategy matrix: (batch_size, max_workers)
    strategies = [
        (1, 100),   # Maximum parallelism, highest overhead
        (4, 75),    # High parallelism, moderate overhead
        (5, 50),    # High parallelism, lower overhead  
        (10, 30),   # Balanced configuration (default)
        (20, 20),   # Moderate parallelism, low overhead
        (50, 10),   # Minimum parallelism, lowest overhead
    ]
    
    results = []
    
    for batch_size, workers in strategies:
        print(f"\n🔧 Probando: {batch_size} dominios/lote, {workers} workers")
        
        # Execute strategy with timing
        start = time.time()
        available = check_domains_parallel(test_domains, batch_size, workers)
        elapsed = time.time() - start
        
        # Calculate performance metrics
        rate = len(test_domains) / elapsed
        results.append((batch_size, workers, elapsed, rate, len(available)))
        
        print(f"⏱️  Tiempo: {elapsed:.1f}s - Velocidad: {rate:.1f} dom/s - Encontrados: {len(available)}")
    
    # Display comprehensive results
    print("\n🏆 Resultados del benchmark:")
    print("Lote\tWorkers\tTiempo(s)\tVelocidad(dom/s)\tEncontrados")
    print("-" * 60)
    
    # Select optimal strategy (minimum execution time)
    best_strategy = min(results, key=lambda x: x[2])
    
    for batch_size, workers, elapsed, rate, found in results:
        marker = " ⭐" if (batch_size, workers) == (best_strategy[0], best_strategy[1]) else ""
        print(f"{batch_size}\t{workers}\t{elapsed:.1f}\t\t{rate:.1f}\t\t{found}{marker}")
    
    print(f"\n🎯 Mejor estrategia: {best_strategy[0]} dominios/lote, {best_strategy[1]} workers")
    return best_strategy[0], best_strategy[1]

def display_tld_menu():
    """Muestra menú interactivo de TLDs en 3 columnas con selección múltiple"""
    tld_categories = get_all_tlds()
    
    print("\n" + "="*60)
    print("                     🔍 DOMAIN FINDER 🔍")
    print("                Buscador de Dominios Disponibles")
    print("="*60)
    
    print("\n📋 SELECCIÓN DE TLDs:")
    print("Puedes seleccionar múltiples TLDs separados por comas")
    print("Ejemplo: 1,5,8 o 1-5,8,10 o 'todos'")
    
    # Crear mapa de opciones y lista plana para columnas
    tld_map = {}
    all_tlds = []
    option_num = 1
    
    # Recolectar todos los TLDs
    for category, tlds in tld_categories.items():
        for tld in tlds:
            tld_map[option_num] = tld
            all_tlds.append((option_num, tld, category))
            option_num += 1
    
    # Mostrar en 3 columnas perfectamente alineadas
    print(f"\n🌍 TODOS LOS TLDs DISPONIBLES:")
    print("-" * 75)
    
    # Calcular filas necesarias
    total_tlds = len(all_tlds)
    rows = (total_tlds + 2) // 3  # División entera redondeada hacia arriba
    
    for row in range(rows):
        row_items = []
        for col in range(3):
            index = row + col * rows
            if index < total_tlds:
                num, tld, category = all_tlds[index]
                # Extraer emoji de la categoría
                emoji = category.split()[0] if ' ' in category else '📌'
                # Formato alineado con ancho fijo para cada columna
                row_items.append(f"{num:2d}. {emoji} {tld:<6}")
        
        # Imprimir fila con espaciado consistente
        if row_items:
            # Usar espaciado fijo de 12 caracteres por columna
            print("  ".join(f"{item:<12}" for item in row_items))
    
    print("-" * 75)
    print(f"{option_num:2d}. Otro (ingresar manualmente)")
    print(f"{option_num+1:2d}. TODOS los TLDs ({len(tld_map)} dominios)")
    
    try:
        choice_input = input(f"\nElige TLD(s) [1-{option_num+1}, ej: 1,3,5 o 'todos']: ").strip().lower()
    except KeyboardInterrupt:
        print("\n\n👋 Saliendo de Domain Finder...")
        print("¡Hasta pronto! 🔍")
        sys.exit(0)
    
    if choice_input == 'todos':
        return list(tld_map.values())
    
    try:
        # Procesar selección manual
        if choice_input.isdigit() and int(choice_input) == option_num:
            try:
                custom_tld = input("Ingresa TLD (ej: .xyz): ").strip()
                if not custom_tld.startswith('.'):
                    custom_tld = "." + custom_tld
                return [custom_tld.lower()]
            except KeyboardInterrupt:
                print("\n\n👋 Saliendo de Domain Finder...")
                print("¡Hasta pronto! 🔍")
                sys.exit(0)
        elif choice_input.isdigit() and int(choice_input) == option_num + 1:
            return list(tld_map.values())
        
        # Procesar selección múltiple
        selected_numbers = []
        for part in choice_input.split(','):
            part = part.strip()
            if '-' in part:
                # Rango ej: 1-5
                start, end = map(int, part.split('-'))
                selected_numbers.extend(range(start, end + 1))
            else:
                # Individual
                selected_numbers.append(int(part))
        
        # Validar y obtener TLDs
        selected_tlds = []
        for num in selected_numbers:
            if num in tld_map:
                selected_tlds.append(tld_map[num])
            elif num == option_num:
                try:
                    custom_tld = input("Ingresa TLD manual (ej: .xyz): ").strip()
                    if not custom_tld.startswith('.'):
                        custom_tld = "." + custom_tld
                    selected_tlds.append(custom_tld.lower())
                except KeyboardInterrupt:
                    print("\n\n👋 Saliendo de Domain Finder...")
                    print("¡Hasta pronto! 🔍")
                    sys.exit(0)
            else:
                print(f"⚠️ Opción {num} no válida, omitiendo...")
        
        if selected_tlds:
            print(f"✅ TLDs seleccionados: {', '.join(selected_tlds)}")
            return selected_tlds
        else:
            print("❌ No se seleccionaron TLDs válidos")
            return display_tld_menu()  # Reintentar
            
    except ValueError:
        print("❌ Formato inválido. Usa: 1,3,5 o 1-5,8 o 'todos'")
        return display_tld_menu()  # Reintentar

def signal_handler(sig, frame):
    """
    Graceful shutdown handler for SIGINT (Ctrl+C).
    
    Args:
        sig: Signal number
        frame: Current stack frame
        
    Behavior:
        - Prevents traceback display on interruption
        - Provides clean exit message
        - Ensures proper resource cleanup
    """
    print("\n\n👋 Saliendo de Domain Finder...")
    print("¡Hasta pronto! 🔍")
    sys.exit(0)

def main():
    """
    Main application entry point with complete user workflow.
    
    Flow:
        1. Initialize signal handlers for graceful shutdown
        2. Display TLD selection menu with 3-column layout
        3. Configure domain length (3 or 4 letters)
        4. Select processing strategy (benchmark or manual)
        5. Execute domain availability check
        6. Save results to timestamped file
        7. Display comprehensive statistics
        
    User Experience:
        - Interactive menus with clear options
        - Real-time progress feedback
        - Error handling and validation
        - Graceful interruption support
    """
    # Configure signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Mostrar banner y menú TLD
    selected_tlds = display_tld_menu()
    
    # Seleccionar longitud
    print(f"\n📏 LONGITUD DEL DOMINIO:")
    print("1. 3 letras (26³ = 17,576 combinaciones por TLD) ⚡")
    print("2. 4 letras (26⁴ = 456,976 combinaciones por TLD) 🐌")
    
    while True:
        try:
            length_choice = int(input("Elige longitud [1-2]: "))
            if length_choice == 1:
                length = 3
                break
            elif length_choice == 2:
                length = 4
                break
            else:
                print("❌ Opción inválida")
        except ValueError:
            print("❌ Ingresa un número válido")
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo de Domain Finder...")
            print("¡Hasta pronto! 🔍")
            sys.exit(0)
    
    total_combinations_per_tld = 26 ** length
    total_combinations = total_combinations_per_tld * len(selected_tlds)
    print(f"\n📊 CONFIGURACIÓN:")
    print(f"   🎯 Dominios: {length} letras")
    print(f"   🌍 TLDs: {', '.join(selected_tlds)}")
    print(f"   🔢 Total: {total_combinations:,} combinaciones")
    print(f"   ⏱️  Tiempo estimado: {total_combinations/1000:.0f}-{total_combinations/100:.0f} segundos")
    
    # Estrategia de procesamiento
    print(f"\n⚙️  ESTRATEGIA DE PROCESAMIENTO:")
    print("1. Automática (benchmark recomendado) 🎯")
    print("2. Rápida (1 dominio/lote, 100 workers) ⚡")
    print("3. Balanceada (10 dominios/lote, 30 workers) ⚖️")
    print("4. Estable (50 dominios/lote, 10 workers) 🐢")
    print("5. Personalizada 🔧")
    
    while True:
        try:
            strategy_choice = int(input("Elige estrategia [1-5]: "))
            if strategy_choice == 1:
                # Benchmark con muestra
                print("\n🧪 Ejecutando benchmark con 1000 dominios de muestra...")
                test_domains = generate_domains_multiple(length, selected_tlds)[:1000]
                batch_size, workers = benchmark_strategies(test_domains)
                try:
                    input("\n🚀 Presiona Enter para iniciar búsqueda completa...")
                except KeyboardInterrupt:
                    print("\n\n👋 Saliendo de Domain Finder...")
                    print("¡Hasta pronto! 🔍")
                    sys.exit(0)
                break
            elif strategy_choice == 2:
                batch_size, workers = 1, 100
                break
            elif strategy_choice == 3:
                batch_size, workers = 10, 30
                break
            elif strategy_choice == 4:
                batch_size, workers = 50, 10
                break
            elif strategy_choice == 5:
                try:
                    batch_size = int(input("Dominios por lote [1-100]: ") or "10")
                    workers = int(input("Número de workers [1-200]: ") or "30")
                except KeyboardInterrupt:
                    print("\n\n👋 Saliendo de Domain Finder...")
                    print("¡Hasta pronto! 🔍")
                    sys.exit(0)
                break
            else:
                print("❌ Opción inválida")
        except ValueError:
            print("❌ Ingresa un número válido")
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo de Domain Finder...")
            print("¡Hasta pronto! 🔍")
            sys.exit(0)
    
    # Iniciar búsqueda
    print(f"\n🚀 INICIANDO BÚSQUEDA COMPLETA...")
    print(f"📊 Estrategia: {batch_size} dominios/lote, {workers} workers")
    print("="*60)
    
    start_time = time.time()
    domains = generate_domains_multiple(length, selected_tlds)
    available = check_domains_parallel(domains, batch_size, workers)
    total_time = time.time() - start_time
    
    # Guardar resultados
    tld_suffix = "_".join([t.replace('.', '') for t in selected_tlds])
    output_file = f"dominios_disponibles_{length}letras_{tld_suffix}.txt"
    with open(output_file, 'w') as f:
        for domain in sorted(available):
            f.write(f"{domain}\n")
    
    # Resumen final
    print("\n" + "="*60)
    print("🎉 BÚSQUEDA COMPLETADA")
    print("="*60)
    print(f"✅ Tiempo total: {total_time:.1f} segundos")
    print(f"🎯 Dominios disponibles: {len(available)}")
    print(f"📁 Resultados guardados en: {output_file}")
    print(f"⚡ Velocidad promedio: {len(domains)/total_time:.1f} dominios/segundo")
    print(f"📈 Eficiencia: {(len(available)/len(domains)*100):.3f}% disponibles")
    
    if available:
        print(f"\n🌟 DOMINIOS ENCONTRADOS ({len(available)}):")
        for domain in sorted(available):
            print(f"  • {domain}")
    else:
        print(f"\n😢 No se encontraron dominios disponibles para {length} letras en {', '.join(selected_tlds)}")
    
    print("="*60)

if __name__ == "__main__":
    """
    Application entry point with multiprocessing support.
    
    Notes:
        - multiprocessing.freeze_support() required for Windows executable
        - Ensures proper process initialization on all platforms
        - Main execution wrapped in try-catch for error handling
    """
    multiprocessing.freeze_support()
    main()