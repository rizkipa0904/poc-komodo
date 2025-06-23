/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { useBus, useService } from "@web/core/utils/hooks";
import { scanBarcode } from "@web/core/barcode/barcode_dialog";
import { isBarcodeScannerSupported } from "@web/core/barcode/barcode_video_scanner";
import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { PlantActivityForm } from "./plant_activity_form";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { Dialog } from "@web/core/dialog/dialog";

export class PlantActivityBarcode extends Component {
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.barcode = useService("barcode"); // Ensure barcode service is used
        console.log("ini event_id", this.props);
        this.state = useState({
            mobileScanner: isBarcodeScannerSupported(),
        });

        onWillStart(async () => {
            console.log("PlantActivityBarcode component is starting...");
        });

        useBus(this.barcode.bus, "barcode_scanned", (ev) => this._onBarcodeScanned(ev.detail.barcode));
    }

    async openMobileScanner() {
        try {
            const barcode = await scanBarcode(this.env, this.facingMode);
            if (barcode) {
                await this._onBarcodeScanned(barcode);
                if ("vibrate" in window.navigator) {
                    window.navigator.vibrate(100);
                }
            } else {
                this.notification.add("Please, Scan again!", { type: "warning" });
            }
        } catch (err) {
            this.notification.add(err.message, { type: "danger" });
        }
    }

    onScanButtonClick() {
        this.openMobileScanner();
    }    

    async _onBarcodeScanned(barcode) {
        console.log("Scanned QR Code:", barcode);
    
        try {
            // Panggil backend untuk mendapatkan batch_id berdasarkan QR code
            const batchResult = await this.orm.call("plant.batch", "get_batch_by_qr", [barcode]);
    
            console.log("Batch Result:", batchResult);
    
            if (!batchResult || !Array.isArray(batchResult) || batchResult.length === 0 || !batchResult[0].id) {
                this.notification.add("Batch not found", { title: "Warning", type: "danger" });
                return;
            }
    
            const batch_id = batchResult[0].batch_number;
            console.log("Batch ID:", batch_id);
    
            // Tampilkan notifikasi sukses jika batch ditemukan
            this.notification.add("Batch found successfully", { title: "Success", type: "success" });

            // Show dialog with batch details
            this.dialogService.add(Dialog, {
                title: "Batch Information",
                body: `
                    <p><strong>Batch Number:</strong> ${batch.batch_number}</p>
                    <p><strong>Name:</strong> ${batch.name}</p>
                    <p><strong>Production Date:</strong> ${batch.production_date || 'N/A'}</p>
                `,
                buttons: [{ text: "Close", close: true }],
            });
    
        } catch (error) {
            console.error("Error in barcode scanning:", error);
            this.notification.add("An error occurred while processing the QR code", { title: "Error", type: "danger" });
        }
    }
    

    onClickBack() {
        this.actionService.doAction("plant_batch_record.action_plant_batch");
    }
}

PlantActivityBarcode.template = "plant_activity_barcode";

registry.category("actions").add("plant_activity_barcode", PlantActivityBarcode);