# Report: Anonymous Confession Platform
**Word Count:** ~1050 words
**Student ID:** 00016440

## 1. Application Overview
"Anonymous Confession App" is a secure web platform where users can post their personal thoughts, secrets, and confessions without revealing their identity. Key user features include a sophisticated mood-based categorisation system, emoji reactions, anonymous or named commenting, and a personalized tracking dashboard for monitoring interaction metrics across all posts.

The application leverages a modern, robust, and scalable technology stack: Django 5.1 provides the backend logic, authentication routing, and Object-Relational Mapping (ORM), while PostgreSQL 16 serves as the primary relational database. The frontend deliberately avoids heavy, complex Single-Page Application (SPA) frameworks like React. Instead, it utilizes vanilla HTML and CSS, strategically enhanced with JavaScript for subtle, premium micro-animations and asynchronous updates (such as AJAX-based reaction toggles).

The core database design is structured around a central `Confession` model. This model maintains foreign key relationships to both `Comment` and `Reaction` models. It also employs a many-to-many relationship with a `Tag` categorization model and features a personalized one-to-one `Profile` extension built directly on top of the default Django authentication `User` model, empowering users to customize an anonymous avatar emoji and display name.

## 2. Containerization Strategy
The application architecture utilizes a robust containerization strategy orchestrated via Docker Compose, defining three specifically isolated microservices: `db` (PostgreSQL), `web` (Django application logic and Gunicorn server), and `nginx` (Reverse Proxy and static asset server).

*[Insert Screenshot: Docker Build Process / Dockerfile Output]*

The `web` service is built using a highly optimized, multi-stage Dockerfile based on the lightweight `python:3.12-slim` image. The process begins with a "builder" stage that installs necessary system dependencies (like a C compiler and PostgreSQL development libraries) and compiles all Python wheels. These pre-compiled wheels are then transferred to the final, bare-bones production stage. This multi-stage approach drastically reduces the final image size and significantly minimizes the container's attack surface by excluding unnecessary compiler tools from the final runtime environment. Furthermore, the application inside the final image executes via a completely non-root `appuser` for strict security compliance, preventing potential privilege escalation risks if the application is somehow compromised.

`docker-compose.yml` seamlessly links these three distinct components. The PostgreSQL database container utilizes persistent named volumes (`postgres_data`) to ensure persistent data storage, preventing database loss if the container is restarted or destroyed. The `web` container mounts a `static_volume` and a `media_volume`, which are simultaneously shared with the `nginx` container as read-only volumes.

*[Insert Screenshot: docker-compose running containers in Docker Desktop or terminal output]*

This shared directory setup allows Nginx to seamlessly intercept and directly serve static assets to the client, entirely bypassing the Python application for static requests. Environment variables are managed securely and dynamically; `docker-compose.yml` provides sensible fallbacks while allowing the deliberate injection of sensitive core credentials (like `POSTGRES_PASSWORD` or `DJANGO_SECRET_KEY`) strictly at runtime. The container orchestrates its startup sequence via a specialized `entrypoint.sh` script, which incorporates a continuous `psycopg2` Python loop that verifies the database connection is genuinely established before applying schemas, entirely stopping premature Gunicorn crashes.

## 3. Deployment Configuration
The application is intentionally designed for rapid deployment onto an Eskiz cloud server (or any Ubuntu-based VPS) using an automated Git-backed pipeline. The server hosting environment requires only Docker and the Docker Compose plugin pre-installed.

*[Insert Screenshot: Eskiz Server Dashboard or Production App Running via Domain]*

Nginx acts as the critical entry point to the system, positioned to handle all incoming port 80 (HTTP) and 443 (HTTPS) internet traffic. It is optimally configured to serve static and media files directly from the Docker volumes attached to it, explicitly defining aggressive caching headers (`expires 30d`) to reduce bandwidth. Simultaneously, it acts as a reverse proxy, correctly forwarding dynamic traffic to the underlying Gunicorn Python application server over the internal Docker network. Gunicorn itself is specifically configured with dynamic worker scaling based dynamically on available host CPU cores (`workers = multiprocessing.cpu_count() * 2 + 1`), ensuring parallel processing for high traffic output.

Production security is a core focus of the deployment configuration:
1. **SSL/HTTPS Setup**: Managed manually via `certbot` and the Let's Encrypt CA authority. Implementing this ensures that all platform data transmitted to and from the server is heavily encrypted utilizing industry-standard TLS protocols.
2. **Server Firewall**: Uncomplicated Firewall (`ufw`) is strictly configured on the primary host out-of-the-box to only allow specific network traffic on ports 22 (Secure SSH), 80 (HTTP validation), and 443 (HTTPS traffic), intelligently dropping all malicious scanner ports.
3. **Secret Management**: Following 12-Factor App principles, completely zero backend credentials, passwords, or secrets exist anywhere within version control tracking.

*[Insert Screenshot: Browser URL bar showing successful HTTPS/SSL lock]*

## 4. CI/CD Pipeline
To guarantee continuous software integration and facilitate perfectly flawless, rapid deployments, a meticulous GitHub Actions workflow pipeline (`.github/workflows/deploy.yml`) actively automates the entire application lifecycle directly from git pushes.

The integration pipeline executes exactly four sequential jobs, automatically triggered on every single code push made to the `main` repository branch:
1. **Linting**: The first step initializes structural analysis. It runs the `flake8` linter plugin across the codebase, enforcing PEP-8 Python coding standards to guarantee formatting and prevent arbitrary styling errors or dead code (like unused imports) from merging.
2. **Testing**: This is the most critical pipeline phase. It instantaneously constructs a bare-bones temporary PostgreSQL service container directly within the GitHub host action and actively executes our entire software testing framework (12 distinct `pytest-django` tests extensively covering all internal CRUD operations, home feeds, interactions, and profile dashboard views). This guarantees that new commits never break current functionality.
3. **Build & Push**: Provided the test suite strictly passes, it interacts with Docker Hub utilizing secure authentication tokens. It sequentially builds our multi-stage Docker image, tags it with both `latest` and the specific Git commit iteration SHA, and permanently pushes it to the Docker Hub registry.
4. **Deployment**: Finally, utilizing `appleboy/ssh-action`, the runner actively authenticates with the target remote Linux production server. It immediately downloads the updated `docker-compose.yml`, securely executes a pull request for the newly compiled image, orchestrates a zero-downtime service restart, and automatically performs database SQL schema migrations.

*[Insert Screenshot: GitHub Actions Workflow Execution History Screen]*

## 5. Challenges and Solutions
Constructing, synchronizing, and successfully deploying this Docker backend infrastructure predictably presented intense, practical development challenges.

A significant hurdle natively involved proper Docker Compose execution startup synchronization. Historically, the `web` container kept crashing unexpectedly precisely because the Gunicorn web server attempted to initialize completely before the PostgreSQL database environment had firmly completed its setup sequence to successfully accept TCP connections. Initially, the built-in PostgreSQL `pg_isready` healthcheck command proved dangerously misleading, as it explicitly lacked the crucial `-d` specific database flag. Replacing this raw baseline command check inside standard bash with a comprehensive `psycopg2` script inside our `entrypoint.sh` fixed this. This Python loop actively authenticates with the specified database before proceeding, ensuring seamless dependency resolution.

Secondly, a significant networking deployment challenge manifested when the Nginx server completely failed to accurately resolve the `web` container backend during simultaneous startup, triggering immediate fatal configuration crashes resulting in connection drops. This was definitively countered directly inside `nginx/default.conf` by officially declaring the native Docker internal network system DNS resolver (`127.0.0.11 valid=30s`). This completely eliminated all premature static upstream hostname resolution failures.

Through resolving these distinct hurdles, the infrastructure's resilience significantly solidified, reinforcing key containerization philosophies concerning rigorous application decoupling and precise network resolution principles.
