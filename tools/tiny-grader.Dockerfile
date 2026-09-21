FROM composer@sha256:e05b92289b813a788b045c8b9cd45831479d071d4615cc8612f1d64935851fd1 AS composer

FROM node@sha256:1b01570a09b39510be11b6d8ac43258d60c68846f26dba191843da614adb226b AS node

FROM moodlehq/moodle-php-apache@sha256:07cac70e0ed3f96f334ffeece92075b98adfbe4110312a3a9308b95eab8e2080

ARG DEBIAN_FRONTEND=noninteractive

COPY --from=composer /usr/bin/composer /usr/local/bin/composer
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client-15=15.19-0+deb12u1 \
        python3=3.11.2-1+b1 \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /usr/local/etc/php/conf.d/docker-php-ext-oci8.ini \
    && ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

ENV COMPOSER_ALLOW_SUPERUSER=1

RUN composer create-project moodlehq/moodle-plugin-ci \
        /opt/moodle-plugin-ci 4.5.11 \
        --no-interaction --no-progress --prefer-dist \
    && test "$(php -r "echo PHP_MAJOR_VERSION.'.'.PHP_MINOR_VERSION;")" = "8.4" \
    && test "$(node --version)" = "v22.11.0" \
    && test "$(npm --version)" = "10.9.0" \
    && test "$(/opt/moodle-plugin-ci/bin/moodle-plugin-ci --version)" = "Moodle Plugin CI 4.5.11" \
    && composer --version \
    && npx --version \
    && git --version \
    && psql --version \
    && python3 --version

ENTRYPOINT []
