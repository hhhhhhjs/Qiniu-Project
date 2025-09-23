FROM openjdk:8
VOLUME /tmp
ADD *.jar app.jar
ENV LANG C.UTF-8
ENV JAVA_OPTS="-Xms256m -Xmx256m -Xmn128m"
ENV LC_ALL C.UTF-8
ENV TZ Asia/Shanghai
RUN ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone
ENTRYPOINT ["java","-Djava.security.egd=file:/dev/./urandom","-jar","/app.jar"]