@echo off

set SPRING_MAIN_BANNER_MODE=off

cd /d ..

set APPTOP=%cd%
set WORKTOP=%cd%
set PP_JAVA_HOME=%APPTOP%\bin\jre
IF EXIST bin\setenv.bat call bin\setenv.bat

set JAVA_HOME=%PP_JAVA_HOME%

call "%JAVA_HOME%\bin\java.exe" --add-modules java.se "-Dtomcat.util.scan.StandardJarScanFilter.jarsToSkip=*.jar" -Xms256m -Xmx6144m -XX:+CMSClassUnloadingEnabled -XX:+HeapDumpOnOutOfMemoryError "-Dcor.configdir=%APPTOP%\conf" "-Dcor.workdir=%WORKTOP%" "-Dcor.logdir=%WORKTOP%\logs" "-Dsolr.log.dir=%WORKTOP%\logs" %JAVA_ARGS_READ_ONLY% "-Djava.util.logging.config.file=%APPTOP%\conf\logging.properties" -Dfile.encoding=UTF8 -Duser.country=us -Duser.language=en -Dhsqldb.method_class_names="" -Dcor.use.tray=false -classpath bin\tomcat\*;bin\pinpoint-standalone.jar com.flatirons.pinpoint.ietpconsole.IetpConsole
