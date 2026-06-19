use std::env;
use std::time::{Duration, Instant};

use dcex::exchanges::binance::BinanceClient;

fn env_positive_usize(name: &str, default: usize) -> usize {
    env::var(name)
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .filter(|value| *value > 0)
        .unwrap_or(default)
}

fn env_nonnegative_usize(name: &str, default: usize) -> usize {
    env::var(name)
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(default)
}

fn mean_duration_ms(values: &[f64]) -> f64 {
    values.iter().sum::<f64>() / values.len() as f64
}

fn median_duration_ms(values: &mut [f64]) -> f64 {
    values.sort_by(|left, right| left.total_cmp(right));
    let midpoint = values.len() / 2;
    if values.len() % 2 == 0 {
        (values[midpoint - 1] + values[midpoint]) / 2.0
    } else {
        values[midpoint]
    }
}

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let iterations = env_positive_usize("DCEX_BENCH_ITERATIONS", 20);
    let warmup = env_nonnegative_usize("DCEX_BENCH_WARMUP", 3);
    let client = BinanceClient::new(None, None, Duration::from_secs(10))?;

    for _ in 0..warmup {
        client.get_server_time("spot").await?;
    }

    let mut elapsed_ms = Vec::with_capacity(iterations);
    for _ in 0..iterations {
        let start = Instant::now();
        client.get_server_time("spot").await?;
        elapsed_ms.push(start.elapsed().as_secs_f64() * 1_000.0);
    }

    let mean = mean_duration_ms(&elapsed_ms);
    let min = elapsed_ms.iter().copied().fold(f64::INFINITY, f64::min);
    let max = elapsed_ms.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    let median = median_duration_ms(&mut elapsed_ms);

    if env::var("DCEX_BENCH_OUTPUT")
        .map(|value| value.eq_ignore_ascii_case("json"))
        .unwrap_or(false)
    {
        println!(
            "{}",
            serde_json::json!({
                "target": "Rust native",
                "iterations": iterations,
                "median_ms": median,
                "mean_ms": mean,
                "min_ms": min,
                "max_ms": max,
            })
        );
    } else {
        println!("| Target | Iterations | Median ms | Mean ms | Min ms | Max ms |");
        println!("| ------ | ---------- | --------- | ------- | ------ | ------ |");
        println!("| Rust native | {iterations} | {median:.3} | {mean:.3} | {min:.3} | {max:.3} |");
    }

    Ok(())
}
