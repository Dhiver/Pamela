file="pam_module"
go build -compiler gccgo -gccgoflags '-static-libgo' -buildmode=c-shared -o ${file}.so
scp -P 2222 pam_module.so root@127.0.0.1:/lib/x86_64-linux-gnu/security/${file}.so
# goPAM="goPAM.a"
# gcc -fPIC -c ${file}.c $goPAM
# gcc -shared -o ${file}.so ${file}.o -lpam
