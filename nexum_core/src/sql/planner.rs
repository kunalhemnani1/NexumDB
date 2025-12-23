use super::types::Statement;

#[derive(Debug, Clone)]
pub enum Plan {
    CreateTable {
        name: String,
        columns: Vec<(String, String)>,
    },
    Insert {
        table: String,
        rows: usize,
    },
    Select {
        table: String,
        columns: Vec<String>,
    },
    Delete {
        table: String,
        has_where: bool,
    },
}

pub struct Planner;

impl Planner {
    pub fn plan(statement: Statement) -> Plan {
        match statement {
            Statement::CreateTable { name, columns } => {
                let cols = columns
                    .iter()
                    .map(|c| (c.name.clone(), format!("{:?}", c.data_type)))
                    .collect();
                Plan::CreateTable {
                    name,
                    columns: cols,
                }
            }
            Statement::Insert { table, values, .. } => Plan::Insert {
                table,
                rows: values.len(),
            },
            Statement::Select { table, columns, .. } => Plan::Select { table, columns },
            Statement::Delete { table, where_clause } => Plan::Delete {
                table,
                has_where: where_clause.is_some(),
            },
        }
    }
}
