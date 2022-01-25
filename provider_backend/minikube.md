# Установка minikube

Для занятий курса вам понадобится установленный и настроенный кластер
Kunernetes. Предлагается использовать для этого установленный локально
[Minikube](http://minikube.sigs.k8s.io/). Ниже приведены инструкции по
установке и запуску кластера для различных ОС. В случае каких-либо
проблем можно обратиться к официальной
[Документации](https://minikube.sigs.k8s.io/docs/start/) проекта.
Также требуются kubectl и helm.

## Подготовка

Для унификации предлагается в качестве гипервизора для запуска
локального кластера использовать
[Virtualbox](https://www.virtualbox.org/). Установите его штаным для
вашей ОС методом.

## Установка ПО

Инсталлятор миникуба настраивает его под окружение. Выберите один из
разделов ниже, соответствующий вашей ОС.

### Linux

```shell
 curl -sLO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && sudo install -m 755 minikube-linux-amd64 /usr/local/bin/minikube
```

и если у вас вдруг ещё не установлен kubectl:

```shell
curl -sLO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl && sudo install -m 755 kubectl /usr/local/bin/kubectl
```

и helm (v3):

```shell
curl -sLO https://get.helm.sh/helm-v3.0.0-linux-amd64.tar.gz
tar xzvf helm-v3.0.0-linux-amd64.tar.gz
sudo install -m 755 linux-amd64/helm /usr/local/bin/helm
```

### MacOS

```shell
brew install minikube helm
```

(установит также и kubectl)

### Windows

Скачайте и запустите
[инсталлятор](https://storage.googleapis.com/minikube/releases/latest/minikube-installer.exe).
Следуйте его инструкциям.

Скачайте
[дистрибутив](https://get.helm.sh/helm-v3.0.0-windows-amd64.zip) helm
и распакуйте исполнимый файл в %PATH%

## Настройка инсталлятора

Драйвер виртуальных машин:
```shell
minikube config set vm-driver virtualbox
```

Так как по умолчанию кластеру выделяется всего 2Гб памяти, необходимо
увеличить это число хотя бы до 4Гб (поставьте больше, если хотите):

```shell
minikube config set memory 4096
```

## Запуск инсталлятора

Выполните:

```shell
minikube start
```

Вы должны получить сообщение о том что kubectl настроен на локальный
кластер minikube (Done! kubectl is now configured to use "minikube")

## Проверка кластера

Для проверки корректности установки дайте следующую команду:

```shell
kubectl get pods -A
```

вы должны получить список подов, все служебные
(etcd/sheduler/apiserver/...) должны быть в состоянии Running.
