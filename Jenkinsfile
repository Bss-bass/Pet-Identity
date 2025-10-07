pipeline {
  agent any

  environment {
    IMAGE_NAME = "siwapatbass/petid"
    TAG = "latest"
    DOCKER_CREDENTIALS = "docker-hub-credentials-id" // Replace with your Docker Hub credentials ID
    DB_NAME = credentials('db-name-id')
    DB_USER = credentials('db-user-id')
    DB_PASSWORD = credentials('db-password-id')
    DJANGO_SECRET_KEY = credentials('django-secret-key-id')
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = "587"
    EMAIL_USE_TLS = "True"
    EMAIL_HOST_USER = credentials('email-host-user-id')
    EMAIL_HOST_PASSWORD = credentials('email-host-password-id')
    DEFAULT_FROM_EMAIL = credentials('default-from-email-id')
    SERVER_IP = "34.158.43.181" // Replace with your actual server IP
    NGROK_DOMAIN = "unslimly-nonarticulative-lindsy.ngrok-free.dev" // Replace with your actual ngrok domain
    COMPOSE_PATH = "/docker-compose.yml"
  }

  stages {
    stage('Clone') {
      steps {
        git branch: 'main', url: 'https://github.com/Bss-bass/Pet-Identity.git'
      }
    }

    stage('Build Docker Image') {
      steps {
        sh "docker build -t $IMAGE_NAME:$TAG ."
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh """
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker push $IMAGE_NAME:$TAG
            docker logout
          """
        }
      }
    }

    stage('Create .env') {
      steps {
        writeFile file: '.env', text: """
          EMAIL_BACKEND=$EMAIL_BACKEND
          EMAIL_HOST=$EMAIL_HOST
          EMAIL_PORT=$EMAIL_PORT
          EMAIL_USE_TLS=$EMAIL_USE_TLS
          EMAIL_HOST_USER=$EMAIL_HOST_USER
          EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD
          DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL
          DB_NAME=$DB_NAME
          DB_USER=$DB_USER
          DB_PASSWORD=$DB_PASSWORD
          DB_HOST=db
          DB_PORT=5432
          SECRET_KEY=$DJANGO_SECRET_KEY
          DEBUG=False
          STATIC_ROOT=/app/static
          MEDIA_ROOT=/app/media
          SERVER_IP=http://$SERVER_IP:8001
          NGROK_DOMAIN=https://$NGROK_DOMAIN
          ALLOWED_HOSTS=localhost,127.0.0.1,$SERVER_IP,$NGROK_DOMAIN
          CSRF_TRUSTED_ORIGINS=http://$SERVER_IP,http://$SERVER_IP:8001,http://$SERVER_IP:8002,https://$NGROK_DOMAIN
        """
      }
    }

    stage('Deploy Local') {
      steps {
        sh """
          cd $WORKSPACE &&
          git pull origin main &&
          docker compose up -d --remove-orphans &&
          docker exec petid_web1 python manage.py collectstatic --noinput &&
          docker exec petid_web2 python manage.py collectstatic --noinput &&
          docker exec petid_web1 python manage.py migrate
        """
      }
    }
  }
}