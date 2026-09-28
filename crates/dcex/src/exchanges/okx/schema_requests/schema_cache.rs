//! Parsed schema cache.
use super::*;

static SCHEMAS: OnceLock<Mutex<HashMap<&'static str, Arc<Value>>>> = OnceLock::new();

pub(super) fn cached_schema(raw: &'static str) -> Result<Arc<Value>> {
    let mut schemas = SCHEMAS
        .get_or_init(|| Mutex::new(HashMap::new()))
        .lock()
        .map_err(|_| invalid("schema cache lock poisoned"))?;
    if let Some(schema) = schemas.get(raw) {
        return Ok(Arc::clone(schema));
    }
    let schema = Arc::new(
        serde_json::from_str(raw).map_err(|error| invalid(&format!("invalid schema: {error}")))?,
    );
    schemas.insert(raw, Arc::clone(&schema));
    Ok(schema)
}

#[cfg(test)]
mod review_cache_tests {
    use super::*;
    #[test]
    fn schema_is_parsed_once_and_shared_between_requests() {
        let first = cached_schema(r#"{"type":"object","review_test":true}"#).unwrap();
        let second = cached_schema(r#"{"type":"object","review_test":true}"#).unwrap();
        assert!(Arc::ptr_eq(&first, &second));
        assert!(cached_schema("invalid schema").is_err());
    }
}
