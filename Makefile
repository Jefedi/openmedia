.PHONY: help install start stop restart logs clean test migrate backup

help: ## Afficher l'aide
	@echo "OpenMedia - Commandes disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installer et démarrer OpenMedia pour la première fois
	@echo "🚀 Installation d'OpenMedia..."
	@if [ ! -f .env ]; then \
		echo "📝 Création du fichier .env..."; \
		cp .env.example .env; \
		echo "⚠️  ATTENTION: Éditez le fichier .env et changez les secrets!"; \
		echo "💡 Exécutez: bash scripts/generate_secrets.sh"; \
		exit 1; \
	fi
	@echo "🐳 Démarrage des conteneurs..."
	docker-compose up -d
	@echo "⏳ Attente que les services soient prêts..."
	sleep 10
	@echo "🗄️  Initialisation de la base de données..."
	docker-compose exec -T api alembic upgrade head
	@echo "✅ Installation terminée!"
	@echo ""
	@echo "🌐 Accédez à l'application:"
	@echo "   Frontend:  http://localhost:3000"
	@echo "   API:       http://localhost:8000"
	@echo "   API Docs:  http://localhost:8000/api/v1/docs"

start: ## Démarrer tous les services
	@echo "🚀 Démarrage d'OpenMedia..."
	docker-compose up -d
	@echo "✅ Services démarrés!"

stop: ## Arrêter tous les services
	@echo "🛑 Arrêt d'OpenMedia..."
	docker-compose down
	@echo "✅ Services arrêtés!"

restart: ## Redémarrer tous les services
	@echo "🔄 Redémarrage d'OpenMedia..."
	docker-compose restart
	@echo "✅ Services redémarrés!"

logs: ## Voir les logs de tous les services
	docker-compose logs -f

logs-api: ## Voir les logs de l'API
	docker-compose logs -f api

logs-worker: ## Voir les logs du worker
	docker-compose logs -f worker

logs-frontend: ## Voir les logs du frontend
	docker-compose logs -f frontend

ps: ## Voir l'état des services
	docker-compose ps

shell-api: ## Accéder au shell de l'API
	docker-compose exec api bash

shell-db: ## Accéder au shell PostgreSQL
	docker-compose exec db psql -U openmedia -d openmedia

shell-redis: ## Accéder au shell Redis
	docker-compose exec redis redis-cli -a $$(grep REDIS_PASSWORD .env | cut -d '=' -f2)

migrate: ## Créer une nouvelle migration
	@read -p "Description de la migration: " desc; \
	docker-compose exec api alembic revision --autogenerate -m "$$desc"

migrate-up: ## Appliquer les migrations
	docker-compose exec api alembic upgrade head

migrate-down: ## Annuler la dernière migration
	docker-compose exec api alembic downgrade -1

test: ## Exécuter les tests
	@echo "🧪 Exécution des tests..."
	docker-compose exec api pytest -v
	@echo "✅ Tests terminés!"

test-cov: ## Exécuter les tests avec coverage
	@echo "🧪 Exécution des tests avec coverage..."
	docker-compose exec api pytest --cov=app --cov-report=html --cov-report=term
	@echo "✅ Coverage report généré dans htmlcov/"

lint: ## Vérifier le code (linting)
	@echo "🔍 Vérification du code backend..."
	docker-compose exec api flake8 app/
	docker-compose exec api black --check app/
	docker-compose exec api isort --check-only app/

format: ## Formater le code
	@echo "✨ Formatage du code backend..."
	docker-compose exec api black app/
	docker-compose exec api isort app/

clean: ## Nettoyer les fichiers temporaires
	@echo "🧹 Nettoyage..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Nettoyage terminé!"

reset: ## Réinitialiser complètement (⚠️ PERTE DE DONNÉES)
	@echo "⚠️  ATTENTION: Cette action va supprimer toutes les données!"
	@read -p "Êtes-vous sûr? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "🗑️  Suppression des conteneurs et volumes..."; \
		docker-compose down -v; \
		echo "✅ Réinitialisation terminée!"; \
		echo "💡 Exécutez 'make install' pour réinstaller"; \
	else \
		echo "❌ Annulé"; \
	fi

backup: ## Créer une sauvegarde de la base de données
	@echo "💾 Création d'une sauvegarde..."
	@mkdir -p backups
	@docker-compose exec -T db pg_dump -U openmedia -d openmedia | gzip > backups/backup_$$(date +%Y%m%d_%H%M%S).sql.gz
	@echo "✅ Sauvegarde créée dans backups/"

restore: ## Restaurer une sauvegarde (spécifier BACKUP=fichier)
	@if [ -z "$(BACKUP)" ]; then \
		echo "❌ Erreur: Spécifiez le fichier de sauvegarde"; \
		echo "Usage: make restore BACKUP=backups/backup_20240101_120000.sql.gz"; \
		exit 1; \
	fi
	@echo "⚠️  ATTENTION: Cette action va écraser les données actuelles!"
	@read -p "Continuer? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "📥 Restauration de $(BACKUP)..."; \
		gunzip < $(BACKUP) | docker-compose exec -T db psql -U openmedia -d openmedia; \
		echo "✅ Restauration terminée!"; \
	else \
		echo "❌ Annulé"; \
	fi

update: ## Mettre à jour le projet
	@echo "🔄 Mise à jour d'OpenMedia..."
	git pull
	docker-compose pull
	docker-compose up -d --build
	docker-compose exec api alembic upgrade head
	@echo "✅ Mise à jour terminée!"

secrets: ## Générer de nouveaux secrets
	@bash scripts/generate_secrets.sh

stats: ## Afficher des statistiques
	@echo "📊 Statistiques OpenMedia"
	@echo ""
	@echo "Services actifs:"
	@docker-compose ps --format "table {{.Name}}\t{{.Status}}"
	@echo ""
	@echo "Utilisation disque:"
	@docker system df
	@echo ""
	@echo "Nombre de films:"
	@docker-compose exec -T db psql -U openmedia -d openmedia -t -c "SELECT COUNT(*) FROM movies;" 2>/dev/null || echo "0 (base non initialisée)"
	@echo "Nombre de séries:"
	@docker-compose exec -T db psql -U openmedia -d openmedia -t -c "SELECT COUNT(*) FROM series;" 2>/dev/null || echo "0 (base non initialisée)"
	@echo "Nombre d'utilisateurs:"
	@docker-compose exec -T db psql -U openmedia -d openmedia -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0 (base non initialisée)"
