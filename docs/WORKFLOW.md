# 🚀 **OFFICIAL Git Workflow & Development Process**

**MANDATORY FOR ALL AI ASSISTANTS AND DEVELOPERS**

## **🔧 Current Branch Strategy (v0.2.07)**

### **Primary Working Model:**
```
main (production-ready)
├── v0.2.07 (current development branch - WORK HERE)
├── v0.2.08 (next version branch - future)
├── feature/consolidated-workflow
├── feature/ai-agents
├── hotfix/critical-fixes
└── bugfix/minor-fixes
```

### **🎯 Branch Hierarchy (ENFORCED)**

1. **`main`** - Production-ready code ONLY
   - Protected branch
   - Merge only via approved PR
   - Requires all checks to pass
   - Tagged releases only

2. **`v0.2.05`** - **CURRENT WORKING BRANCH**
   - **All AI assistants work here**
   - Feature development base
   - Quality-assured code
   - Ready for production merge

3. **`feature/description`** - Feature development
   - Created from `v0.2.05`
   - Lifespan: 1-3 days MAX
   - Merge back to `v0.2.05`
   - Auto-deleted after merge

4. **`hotfix/description`** - Critical fixes
   - Created from `main` or `v0.2.05`
   - Lifespan: Hours to 1 day
   - Immediate merge priority

### **📋 MANDATORY Branch Naming Convention**

```bash
# Feature branches
feature/compact-html-export
feature/ml-sentiment-analysis
feature/api-authentication

# Bug fixes
bugfix/story-parsing-error
bugfix/memory-leak-fix
bugfix/cli-argument-validation

# Hotfixes
hotfix/security-vulnerability
hotfix/data-corruption-fix
hotfix/performance-critical-fix

# Performance improvements
perf/json-parsing-optimization
perf/memory-usage-reduction
perf/database-query-optimization
```

### 🕒 Frecuencia de Merge

#### Merge Automático Diario
- **Features pequeñas**: Merge cada 24-48 horas
- **Features medianas**: Merge cada 3-5 días
- **Features grandes**: Dividir en sub-features más pequeñas

#### Merge a Main (Releases)
- **Releases menores**: Cada 1-2 semanas
- **Releases mayores**: Cada 3-4 semanas
- **Hotfixes**: Inmediato

### 🛠️ Flujo de Trabajo Paso a Paso

#### 1. Inicio de Feature
```bash
# Configurar git automation (una vez)
make git-setup

# Crear nueva feature branch
make branch-new
# o directamente:
git feat "Add compact HTML reports"
```

#### 2. Desarrollo Activo
```bash
# Mientras desarrollas
make test          # Ejecutar tests
make quality       # Verificar calidad
git add .
git commit -m "feat: implement data pagination"  # Auto-formateado
```

#### 3. Preparación para Merge
```bash
# Verificar que todo esté listo
make pr-ready      # Ejecuta CI completo
git push origin feat/compact-reports-20250718
```

#### 4. Pull Request
- Crear PR en GitHub
- Revisión automática por CI
- Revisión manual por equipo
- Merge automático si pasa todas las verificaciones

### 📊 Criterios de Merge

#### Merge Automático (Si cumple):
- ✅ Todos los tests pasan (88%+ success rate)
- ✅ Cobertura de código >80%
- ✅ Linting y type checking sin errores
- ✅ Security checks aprobados
- ✅ Documentación actualizada

#### Merge Manual (Requiere revisión):
- ⚠️ Cambios en arquitectura core
- ⚠️ Nuevas dependencias
- ⚠️ Cambios en API pública
- ⚠️ Modificaciones de configuración

### 🎯 Estrategia por Tipo de Cambio

#### Features (70% del desarrollo)
```bash
# Rama de vida corta: 1-3 días
git feat "Add ML sentiment analysis"
# Desarrollo iterativo
git commit -m "feat: implement TextBlob integration"
git commit -m "feat: add emotion detection"
git commit -m "feat: integrate with main analyzer"
# Merge rápido a develop
```

#### Optimizaciones (20% del desarrollo)
```bash
# Rama de vida muy corta: horas/1 día
git perf "Optimize memory usage in JSON parsing"
# Cambios focalizados
git commit -m "perf: implement streaming JSON parser"
git commit -m "perf: add memory profiling"
# Merge inmediato
```

#### Bugfixes (10% del desarrollo)
```bash
# Rama de vida inmediata: horas
git fix "Fix story count showing zero"
# Corrección directa
git commit -m "fix: correct Pydantic validation in Media model"
# Merge inmediato a develop o main
```

### 📈 Métricas de Flujo

#### Objetivos de Velocidad
- **Feature branches**: Max 3 días de vida
- **Commits por día**: 3-5 commits pequeños
- **PRs por semana**: 5-7 PRs
- **Merge rate**: 95% de PRs aprobados automáticamente

#### Métricas de Calidad
- **Test success rate**: >88% (actual)
- **Code coverage**: >80% (objetivo)
- **Security issues**: 0 críticos
- **Documentation**: 100% APIs documentadas

### 🔄 Ciclo de Vida de una Feature

```mermaid
graph TD
    A[Crear feature branch] --> B[Desarrollo iterativo]
    B --> C[Commits pequeños y frecuentes]
    C --> D[Tests y quality checks]
    D --> E[Push a origin]
    E --> F[Create Pull Request]
    F --> G[CI/CD Automático]
    G --> H[Code Review]
    H --> I[Merge a develop]
    I --> J[Deploy a staging]
    J --> K[Merge a main]
    K --> L[Deploy a production]
```

### 🚀 Comandos Esenciales

#### Setup Inicial
```bash
# Configurar entorno completo
make setup-dev

# Instalar git automation
make git-setup
```

#### Desarrollo Diario
```bash
# Crear nueva feature
make branch-new

# Verificar durante desarrollo
make quick-check

# Preparar para commit
make commit-ready

# Preparar para PR
make pr-ready
```

#### Monitoreo
```bash
# Ver historial de branches
make branch-history

# Estado actual
make status

# Configuración
make git-config
```

## **🤖 Automated CI/CD & Multi-Agent Workflow**

### **Consolidated Workflow Architecture**

The project now uses a **consolidated workflow system** that integrates:
- CI/CD pipeline
- ML pipeline
- Multi-agent AI system

See [CONSOLIDATED_WORKFLOW.md](CONSOLIDATED_WORKFLOW.md) for details on the integrated system.

### **AI Multi-Agent CI/CD Workflow**

The project uses a **consolidated workflow** (`main-workflow.yml`) that integrates CI/CD, ML Pipeline, and a multi-agent AI system:

#### **Consolidated Workflow Components:**

1. **CI/CD Pipeline**
   - Testing with multiple Python versions
   - Security analysis and vulnerability scanning
   - Type checking with MyPy
   - Documentation generation with Sphinx
   - Package building and distribution

2. **ML Pipeline**
   - Model training and validation
   - Performance benchmarking
   - Artifact generation and storage

3. **AI Multi-Agent System**
   - **AI Orchestrator** - Analyzes issues/PRs and routes to specialized agents
   - **AI Code Review** - Static analysis, quality checks, automated improvements
   - **AI Documentation** - Documentation coverage analysis and improvements
   - **AI Testing** - Test coverage analysis and test generation
   - **AI Optimization** - Performance analysis and optimization recommendations
   - **AI Feature** - Feature implementation planning and code generation

### **Workflow Usage Examples:**

1. **Code Review Example:**
   ```
   1. Developer creates PR with code changes
   2. Orchestrator analyzes content and adds `ai:review` label
   3. AI Review agent runs static analysis and comments findings
   4. If there are automatic fixes, a new PR is created
   5. Team reviews and approves suggested changes
   ```

2. **Feature Request Example:**
   ```
   1. Developer creates issue with feature description
   2. Orchestrator analyzes content and adds `ai:feature` label
   3. AI Feature agent creates implementation plan
   4. Agent generates code skeleton in a new branch
   5. Developer and agent collaborate to complete implementation
   ```

Para detalles y troubleshooting completos, ver la sección "Automated Multi-Agent Workflows" en el README.

### 🎨 Estrategia de Releases

#### Versioning Automático
- **Patch** (0.2.X): Bugfixes, optimizaciones menores
- **Minor** (0.X.0): Nuevas features, mejoras
- **Major** (X.0.0): Cambios arquitectónicos, breaking changes

#### Release Schedule
- **Sprints**: 2 semanas
- **Minor releases**: Cada sprint
- **Major releases**: Cada 2-3 meses
- **Hotfixes**: Según necesidad

### 📋 Checklist de Desarrollo

#### Antes de Commitear
- [ ] Tests pasan localmente
- [ ] Linting sin errores
- [ ] Type checking correcto
- [ ] Documentación actualizada

#### Antes de PR
- [ ] CI completo pasa
- [ ] Cobertura mantenida
- [ ] Security checks OK
- [ ] Changelog actualizado

#### Antes de Merge
- [ ] Revisión de código
- [ ] Tests de integración
- [ ] Performance no degradada
- [ ] Compatibilidad verificada

### 🎯 Beneficios del Flujo

1. **Velocidad**: Merges rápidos y frecuentes
2. **Calidad**: Verificación automática continua
3. **Trazabilidad**: Historial completo de cambios
4. **Reversibilidad**: Fácil rollback si hay problemas
5. **Colaboración**: Flujo claro para todo el equipo

### 🔧 Personalización

El sistema es configurable via `.git-automation.json`:

```json
{
  "base_branch": "main",
  "auto_version": true,
  "merge_frequency": "daily",
  "require_tests": true,
  "auto_cleanup": true
}
```

### 📞 Soporte

Si tienes dudas sobre el flujo:
1. Consulta `make workflow-example`
2. Revisa `make branch-history`
3. Usa `make branch-new` para workflow interactivo

Este flujo garantiza desarrollo ágil manteniendo la calidad enterprise que caracteriza al proyecto.
