use nexum_core::{Executor, Parser, StorageEngine};

#[test]
fn test_advanced_sql_features() {
    let storage = StorageEngine::memory().unwrap();
    let executor = Executor::new(storage);

    let create =
        Parser::parse("CREATE TABLE items (id INTEGER, name TEXT, price INTEGER)").unwrap();
    executor.execute(create).unwrap();

    let insert = Parser::parse(
        "INSERT INTO items (id, name, price) VALUES (1, 'TestA', 100), (2, 'TestB', 200), (3, 'OtherC', 50), (4, 'TestC', 150)"
    ).unwrap();
    executor.execute(insert).unwrap();

    let select =
        Parser::parse("SELECT * FROM items WHERE name LIKE 'Test%' ORDER BY price DESC LIMIT 2")
            .unwrap();
    let result = executor.execute(select).unwrap();

    match result {
        nexum_core::executor::ExecutionResult::Selected { rows, .. } => {
            println!("Result rows: {:?}", rows);
            assert_eq!(rows.len(), 2);
        }
        _ => panic!("Expected Selected result"),
    }
}

#[test]
fn test_in_operator_integration() {
    let storage = StorageEngine::memory().unwrap();
    let executor = Executor::new(storage);

    let create = Parser::parse("CREATE TABLE orders (id INTEGER, status TEXT)").unwrap();
    executor.execute(create).unwrap();

    let insert = Parser::parse(
        "INSERT INTO orders VALUES (1, 'active'), (2, 'pending'), (3, 'completed'), (4, 'active')",
    )
    .unwrap();
    executor.execute(insert).unwrap();

    let select =
        Parser::parse("SELECT * FROM orders WHERE status IN ('active', 'pending')").unwrap();
    let result = executor.execute(select).unwrap();

    match result {
        nexum_core::executor::ExecutionResult::Selected { rows, .. } => {
            assert_eq!(rows.len(), 3);
        }
        _ => panic!("Expected Selected result"),
    }
}

#[test]
fn test_between_with_order_limit() {
    let storage = StorageEngine::memory().unwrap();
    let executor = Executor::new(storage);

    let create = Parser::parse("CREATE TABLE products (id INTEGER, price INTEGER)").unwrap();
    executor.execute(create).unwrap();

    let insert = Parser::parse(
        "INSERT INTO products VALUES (1, 50), (2, 150), (3, 250), (4, 175), (5, 125)",
    )
    .unwrap();
    executor.execute(insert).unwrap();

    let select = Parser::parse(
        "SELECT * FROM products WHERE price BETWEEN 100 AND 200 ORDER BY price ASC LIMIT 3",
    )
    .unwrap();
    let result = executor.execute(select).unwrap();

    match result {
        nexum_core::executor::ExecutionResult::Selected { rows, .. } => {
            assert_eq!(rows.len(), 3);
        }
        _ => panic!("Expected Selected result"),
    }
}
