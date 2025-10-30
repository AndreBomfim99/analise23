"""
Data Validation - Olist E-Commerce
-----------------------------------
Validações de qualidade de dados após ETL para BigQuery.
Detecta anomalias, valores faltantes, duplicatas e inconsistências.

Autor: Andre Bomfim
Data: Outubro 2025
"""

import os
import sys
from typing import Dict, List, Tuple
from datetime import datetime
import pandas as pd
from google.cloud import bigquery
from loguru import logger

# Configuração de logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/data_validation.log", rotation="10 MB", level="DEBUG")


class DataValidator:
    """Validador de qualidade de dados no BigQuery"""
    
    def __init__(self, project_id: str, dataset_id: str):
        """
        Inicializa o validador
        
        Args:
            project_id: ID do projeto GCP
            dataset_id: ID do dataset BigQuery
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        self.validation_results = []
        
        logger.info(f"Validator inicializado: {project_id}.{dataset_id}")
    
    def _run_validation_query(self, test_name: str, query: str, 
                             expected_value: any = 0, 
                             operator: str = "==") -> Dict:
        """
        Executa uma query de validação
        
        Args:
            test_name: Nome do teste
            query: Query SQL
            expected_value: Valor esperado
            operator: Operador de comparação (==, >, <, <=, >=)
            
        Returns:
            Dict com resultado do teste
        """
        try:
            result = self.client.query(query).to_dataframe()
            actual_value = result.iloc[0, 0]
            
            # Avaliar condição
            if operator == "==":
                passed = actual_value == expected_value
            elif operator == ">":
                passed = actual_value > expected_value
            elif operator == "<":
                passed = actual_value < expected_value
            elif operator == "<=":
                passed = actual_value <= expected_value
            elif operator == ">=":
                passed = actual_value >= expected_value
            else:
                passed = False
            
            status = "✅ PASS" if passed else "❌ FAIL"
            
            validation = {
                "test_name": test_name,
                "status": status,
                "expected": expected_value,
                "actual": actual_value,
                "passed": passed,
                "timestamp": datetime.now()
            }
            
            self.validation_results.append(validation)
            
            if passed:
                logger.success(f"{status} - {test_name}: {actual_value}")
            else:
                logger.error(f"{status} - {test_name}: Expected {expected_value}, Got {actual_value}")
            
            return validation
            
        except Exception as e:
            logger.error(f"Erro no teste '{test_name}': {str(e)}")
            return {
                "test_name": test_name,
                "status": "⚠️ ERROR",
                "error": str(e),
                "passed": False,
                "timestamp": datetime.now()
            }
    
    # =========================================
    # TESTES DE INTEGRIDADE REFERENCIAL
    # =========================================
    
    def test_primary_keys(self) -> List[Dict]:
        """Testa se primary keys são únicas e não nulas"""
        
        logger.info("Testando Primary Keys...")
        
        tests = [
            # Customers
            {
                "name": "customers: customer_id único",
                "query": f"""
                    SELECT COUNT(*) - COUNT(DISTINCT customer_id) 
                    FROM `{self.project_id}.{self.dataset_id}.customers`
                """
            },
            {
                "name": "customers: customer_id não nulo",
                "query": f"""
                    SELECT COUNTIF(customer_id IS NULL)
                    FROM `{self.project_id}.{self.dataset_id}.customers`
                """
            },
            
            # Orders
            {
                "name": "orders: order_id único",
                "query": f"""
                    SELECT COUNT(*) - COUNT(DISTINCT order_id)
                    FROM `{self.project_id}.{self.dataset_id}.orders`
                """
            },
            {
                "name": "orders: order_id não nulo",
                "query": f"""
                    SELECT COUNTIF(order_id IS NULL)
                    FROM `{self.project_id}.{self.dataset_id}.orders`
                """
            },
            
            # Order Items (composite key)
            {
                "name": "order_items: (order_id, order_item_id) único",
                "query": f"""
                    SELECT COUNT(*) - COUNT(DISTINCT CONCAT(order_id, '-', CAST(order_item_id AS STRING)))
                    FROM `{self.project_id}.{self.dataset_id}.order_items`
                """
            },
        ]
        
        for test in tests:
            self._run_validation_query(test["name"], test["query"], expected_value=0)
    
    def test_foreign_keys(self) -> List[Dict]:
        """Testa integridade de foreign keys"""
        
        logger.info("Testando Foreign Keys...")
        
        tests = [
            {
                "name": "orders.customer_id existe em customers",
                "query": f"""
                    SELECT COUNT(*)
                    FROM `{self.project_id}.{self.dataset_id}.orders` o
                    LEFT JOIN `{self.project_id}.{self.dataset_id}.customers` c
                      ON o.customer_id = c.customer_id
                    WHERE c.customer_id IS NULL
                """
            },
            {
                "name": "order_items.order_id existe em orders",
                "query": f"""
                    SELECT COUNT(*)
                    FROM `{self.project_id}.{self.dataset_id}.order_items` oi
                    LEFT JOIN `{self.project_id}.{self.dataset_id}.orders` o
                      ON oi.order_id = o.order_id
                    WHERE o.order_id IS NULL
                """
            },
            {
                "name": "order_items.product_id existe em products",
                "query": f"""
                    SELECT COUNT(*)
                    FROM `{self.project_id}.{self.dataset_id}.order_items` oi
                    LEFT JOIN `{self.project_id}.{self.dataset_id}.products` p
                      ON oi.product_id = p.product_id
                    WHERE p.product_id IS NULL
                """
            },
            {
                "name": "payments.order_id existe em orders",
                "query": f"""
                    SELECT COUNT(*)
                    FROM `{self.project_id}.{self.dataset_id}.payments` p
                    LEFT JOIN `{self.project_id}.{self.dataset_id}.orders` o
                      ON p.order_id = o.order_id
                    WHERE o.order_id IS NULL
                """
            },
        ]
        
        for test in tests:
            self._run_validation_query(test["name"], test["query"], expected_value=0)
    
    # =========================================
    # TESTES DE VALORES VÁLIDOS
    # =========================================
    
    def test_valid_values(self) -> List[Dict]:
        """Testa se valores estão dentro de ranges válidos"""
        
        logger.info("Testando Valores Válidos...")
        
        tests = [
            # Preços positivos
            {
                "name": "order_items: price >= 0",
                "query": f"""
                    SELECT COUNTIF(price < 0)
                    FROM `{self.project_id}.{self.dataset_id}.order_items`
                """
            },
            {
                "name": "order_items: freight_value >= 0",
                "query": f"""
                    SELECT COUNTIF(freight_value < 0)
                    FROM `{self.project_id}.{self.dataset_id}.order_items`
                """
            },
            {
                "name": "payments: payment_value > 0",
                "query": f"""
                    SELECT COUNTIF(payment_value <= 0)
                    FROM `{self.project_id}.{self.dataset_id}.payments`
                """
            },
            
            # Review scores válidos (1-5)
            {
                "name": "reviews: review_score entre 1 e 5",
                "query": f"""
                    SELECT COUNTIF(review_score < 1 OR review_score > 5)
                    FROM `{self.project_id}.{self.dataset_id}.reviews`
                    WHERE review_score IS NOT NULL
                """
            },
            
            # Estados válidos (26 UFs + DF)
            {
                "name": "customers: customer_state válido (27 estados)",
                "query": f"""
                    SELECT COUNT(DISTINCT customer_state)
                    FROM `{self.project_id}.{self.dataset_id}.customers`
                    WHERE customer_state NOT IN (
                        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
                        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
                        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
                    )
                """
            },
            
            # Order status válidos
            {
                "name": "orders: order_status válido",
                "query": f"""
                    SELECT COUNTIF(order_status NOT IN (
                        'delivered', 'shipped', 'canceled', 'unavailable', 
                        'invoiced', 'processing', 'created', 'approved'
                    ))
                    FROM `{self.project_id}.{self.dataset_id}.orders`
                """
            },
        ]
        
        for test in tests:
            self._run_validation_query(test["name"], test["query"], expected_value=0)
    
    # =========================================
    # TESTES DE COMPLETUDE
    # =========================================
    
    def test_completeness(self) -> List[Dict]:
        """Testa % de valores faltantes em colunas críticas"""
        
        logger.info("Testando Completude de Dados...")
        
        tests = [
            {
                "name": "orders: order_purchase_timestamp não nulo (>99%)",
                "query": f"""
                    SELECT COUNTIF(order_purchase_timestamp IS NOT NULL) / COUNT(*) * 100
                    FROM `{self.project_id}.{self.dataset_id}.orders`
                """,
                "expected": 99,
                "operator": ">"
            },
            {
                "name": "products: product_category_name não nulo (>95%)",
                "query": f"""
                    SELECT COUNTIF(product_category_name IS NOT NULL) / COUNT(*) * 100
                    FROM `{self.project_id}.{self.dataset_id}.products`
                """,
                "expected": 95,
                "operator": ">"
            },
            {
                "name": "orders delivered: tem data de entrega (>95%)",
                "query": f"""
                    SELECT COUNTIF(order_delivered_customer_date IS NOT NULL) / COUNT(*) * 100
                    FROM `{self.project_id}.{self.dataset_id}.orders`
                    WHERE order_status = 'delivered'
                """,
                "expected": 95,
                "operator": ">"
            },
        ]
        
        for test in tests:
            self._run_validation_query(
                test["name"], 
                test["query"], 
                expected_value=test.get("expected", 0),
                operator=test.get("operator", "==")
            )
    
    # =========================================
    # TESTES DE CONSISTÊNCIA
    # =========================================
    
    def test_consistency(self) -> List[Dict]:
        """Testa consistência lógica entre campos"""
        
        logger.info("Testando Consistência Lógica...")
        
        tests = [
            {
                "name": "orders: data de compra < data de entrega",
                "query": f"""
                    SELECT COUNTIF(order_purchase_timestamp >= order_delivered_customer_date)
                    FROM `{self.project_id}.{self.dataset_id}.orders`
                    WHERE order_delivered_customer_date IS NOT NULL
                """
            },
            {
                "name": "orders: data estimada >= data de compra",
                "query": f"""
                    SELECT COUNTIF(order_estimated_delivery_date < order_purchase_timestamp)
                    FROM `{self.project_id}.{self.dataset_id}.orders`
                    WHERE order_estimated_delivery_date IS NOT NULL
                """
            },
            {
                "name": "payments: soma por pedido = order_value (diferença <1%)",
                "query": f"""
                    WITH payment_totals AS (
                        SELECT 
                            order_id,
                            SUM(payment_value) as total_paid
                        FROM `{self.project_id}.{self.dataset_id}.payments`
                        GROUP BY order_id
                    ),
                    item_totals AS (
                        SELECT 
                            order_id,
                            SUM(price + freight_value) as total_items
                        FROM `{self.project_id}.{self.dataset_id}.order_items`
                        GROUP BY order_id
                    )
                    SELECT COUNTIF(ABS(pt.total_paid - it.total_items) > it.total_items * 0.01)
                    FROM payment_totals pt
                    INNER JOIN item_totals it ON pt.order_id = it.order_id
                """
            },
        ]
        
        for test in tests:
            self._run_validation_query(test["name"], test["query"], expected_value=0)
    
    # =========================================
    # TESTES DE VOLUMETRIA
    # =========================================
    
    def test_volumetry(self) -> List[Dict]:
        """Testa volumes esperados de dados"""
        
        logger.info("Testando Volumetria...")
        
        tests = [
            {
                "name": "customers: tem registros (>90k)",
                "query": f"""
                    SELECT COUNT(*)
                    FROM `{self.project_id}.{self.dataset_id}.customers`
                """,
                "expected": 90000,
                "operator": ">"
            },
            {
                "name": "orders: tem registros (>90k)",
                "query": f"""
                    SELECT COUNT(*)
                    FROM `{self.project_id}.{self.dataset_id}.orders`
                """,
                "expected": 90000,
                "operator": ">"
            },
            {
                "name": "order_items: tem mais itens que orders",
                "query": f"""
                    SELECT 
                        (SELECT COUNT(*) FROM `{self.project_id}.{self.dataset_id}.order_items`) -
                        (SELECT COUNT(*) FROM `{self.project_id}.{self.dataset_id}.orders`)
                """,
                "expected": 0,
                "operator": ">"
            },
            {
                "name": "orders delivered: >90% do total",
                "query": f"""
                    SELECT COUNTIF(order_status = 'delivered') / COUNT(*) * 100
                    FROM `{self.project_id}.{self.dataset_id}.orders`
                """,
                "expected": 90,
                "operator": ">"
            },
        ]
        
        for test in tests:
            self._run_validation_query(
                test["name"], 
                test["query"], 
                expected_value=test.get("expected", 0),
                operator=test.get("operator", "==")
            )
    
    # =========================================
    # MÉTODO PRINCIPAL
    # =========================================
    
    def run_all_validations(self) -> pd.DataFrame:
        """
        Executa todas as validações
        
        Returns:
            DataFrame com resultados
        """
        logger.info("=" * 60)
        logger.info("INICIANDO VALIDAÇÃO DE DADOS")
        logger.info("=" * 60)
        
        # Executar todos os testes
        self.test_primary_keys()
        self.test_foreign_keys()
        self.test_valid_values()
        self.test_completeness()
        self.test_consistency()
        self.test_volumetry()
        
        # Consolidar resultados
        df_results = pd.DataFrame(self.validation_results)
        
        # Sumário
        total_tests = len(df_results)
        passed_tests = df_results['passed'].sum()
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info("\n" + "=" * 60)
        logger.info("SUMÁRIO DE VALIDAÇÃO")
        logger.info("=" * 60)
        logger.info(f"Total de testes: {total_tests}")
        logger.info(f"✅ Testes passados: {passed_tests}")
        logger.info(f"❌ Testes falhos: {failed_tests}")
        logger.info(f"Taxa de sucesso: {success_rate:.2f}%")
        
        if failed_tests > 0:
            logger.warning("\nTestes que falharam:")
            for _, row in df_results[~df_results['passed']].iterrows():
                logger.warning(f"  - {row['test_name']}")
        
        # Salvar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"data/processed/validation_results_{timestamp}.csv"
        df_results.to_csv(output_file, index=False)
        logger.success(f"\n✓ Resultados salvos em: {output_file}")
        
        return df_results


def main():
    """Função principal"""
    
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    project_id = os.getenv('GCP_PROJECT_ID')
    dataset_id = os.getenv('GCP_DATASET_ID', 'olist_ecommerce')
    
    # Validar configuração
    if not project_id:
        logger.error("GCP_PROJECT_ID não definido no .env")
        sys.exit(1)
    
    # Executar validações
    validator = DataValidator(project_id, dataset_id)
    results = validator.run_all_validations()
    
    # Exit code baseado no resultado
    if results['passed'].all():
        logger.success("\n🎉 Todas as validações passaram!")
        sys.exit(0)
    else:
        logger.error("\n⚠️ Algumas validações falharam. Revise os logs.")
        sys.exit(1)


if __name__ == "__main__":
    main()