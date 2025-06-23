# Gunakan image resmi Odoo versi 16
FROM odoo:16.0

LABEL maintainer="yourname@example.com"

# Gunakan root untuk install tambahan
USER root

RUN apt-get update && apt-get install -y \
    nano vim git \
    && rm -rf /var/lib/apt/lists/*

# Salin custom module ke folder addons Odoo
COPY ./custom_addons /mnt/extra-addons

# Ubah kepemilikan supaya bisa diakses user odoo
RUN chown -R odoo:odoo /mnt/extra-addons

# Salin konfigurasi Odoo
COPY ./odoo.conf /etc/odoo/odoo.conf

# Kembali ke user odoo
USER odoo
