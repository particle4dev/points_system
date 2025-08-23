## Setup mutagen for DO

```sh
mutagen sync list

mutagen sync create -n=points-system -c=./mutagen.yml ./ root@146.190.4.129:~/workspace/points-system
```

If you want to delete agent

```sh
mutagen sync terminate points-system
```

Connect to ec2

```sh
ssh -i ~/.ssh/id_rsa -p 22 root@146.190.4.129
```
