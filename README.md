# INE5418-05208-T2

Para executar o programa

É necessário rodar primeiro o servidor zookeeper:
1 - para isso é preciso garantir que o terminal se localiza na pasta ./apache-zookeeper-3.9.2-bin
2 - e então rodar o comando: bin/zkServer.sh start-foreground conf1/zoo.cfg
3 - esses passos devem ser repetidos mais 2 vezes alterando apenas a pasta de configuração passada no comando em (2) para conf2 e conf3
Caso haja algum problema com o zookeeper pode ser necessária a reeinstalação:
1 - baixar o zookeeper no site oficial: https://zookeeper.apache.org/releases.html
2 - descompactar o arquivo, caso necessário, e colocar a pasta no ambiente desejado
3 - criar as três pastas de configurações usadas (conf1, conf2, conf3)
4 - em cada uma das pastas criar o arquivo zoo.cfg que deve ser preenchido da seguinte forma:

# The number of milliseconds of each tick
tickTime=2000
# The number of ticks that the initial 
# synchronization phase can take
initLimit=5
# The number of ticks that can pass between 
# sending a request and getting an acknowledgement
syncLimit=2
# the directory where the snapshot is stored.
# do not use /tmp for storage, /tmp here is just 
# example sakes.
dataDir=./data1
# the port at which the clients will connect
clientPort=2181
# the maximum number of client connections.
# increase this if you need to handle more clients
#maxClientCnxns=60
#
# Be sure to read the maintenance section of the 
# administrator guide before turning on autopurge.
#
# https://zookeeper.apache.org/doc/current/zookeeperAdmin.html#sc_maintenance
#
# The number of snapshots to retain in dataDir
#autopurge.snapRetainCount=3
# Purge task interval in hours
# Set to "0" to disable auto purge feature
#autopurge.purgeInterval=1

## Metrics Providers
#
# https://prometheus.io Metrics Exporter
#metricsProvider.className=org.apache.zookeeper.metrics.prometheus.PrometheusMetricsProvider
#metricsProvider.httpHost=0.0.0.0
#metricsProvider.httpPort=7000
#metricsProvider.exportJvmInfo=true
server.1=localhost:2666:3666
server.2=localhost:2667:3667
server.3=localhost:2668:3668

5- a configuração clientPort deve ser editada de acordo com qual replica recebe esse documento de configuração \
de modo que o último digito da port seja o mesmo da pasta (o cliente kazoo acessa o servidor por essas portas)
6 - criar as três pastas para dados do servidor (data1, data2, data3)
7 - incluir em cada uma dessas pastas um arquivo myid contendo apenas o id do servidor (1, 2, 3)
8 - rodar o servidor como descrito previamente

Com o servidor em execução basta executar o código em python
comando: python3 app.py
Cada processo app irá criar seu próprio nodo
Como nenhum id é expecificado na inicialização cada nodo adota id n+1, onde n é o número de znodes filhos da raíz no momento da inicialização da nova instância da classe Node
