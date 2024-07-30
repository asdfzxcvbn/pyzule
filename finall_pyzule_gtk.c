#include <gtk/gtk.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

GtkWidget *file_dialog;
GtkWidget *output_dialog;
GtkWidget *files_dialog;
GtkWidget *arg_disable_compression;
GtkWidget *arg_remove_uisupporteddevices;
GtkWidget *arg_remove_watch_app;
GtkWidget *arg_enable_files_access;
GtkWidget *file_label;
GtkWidget *output_label;
GtkWidget *files_label;
GtkWidget *arg_remove_app_extensions;
GtkWidget *arg_remove_encrypted_extensions;
GtkWidget *arg_substitute_instead_of_substrate;
GtkWidget *arg_arm_bin4arm64;
GtkWidget *fakesigns_ipa;
GtkWidget *advance_box;
GtkWidget *version_entry;
GtkWidget *name_entry;
GtkWidget *bundle_id_entry;
GtkWidget *min_os_entry;
GtkWidget *advance_button;
GtkWidget *arg_version;
GtkWidget *arg_name;
GtkWidget *arg_bundle_id;
GtkWidget *arg_min_os;

void run_pyzule(GtkWidget *widget, gpointer data) {
    GtkFileChooser *chooser = GTK_FILE_CHOOSER(file_dialog);
    GtkFileChooser *output_chooser_widget = GTK_FILE_CHOOSER(output_dialog);
    char *file_path = gtk_file_chooser_get_filename(chooser);
    char *output_path = gtk_file_chooser_get_filename(output_chooser_widget);

    GSList *file_list = gtk_file_chooser_get_filenames(GTK_FILE_CHOOSER(files_dialog));
    GSList *l;
    char files_arg[1024] = "";
    for (l = file_list; l != NULL; l = l->next) {
        char *filename = (char *) l->data;
        strcat(files_arg, filename);
        strcat(files_arg, " ");
        g_free(filename);
    }

    char args[1024] = "";
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(arg_disable_compression))) {
        strcat(args, "-c 0 ");
    }
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(arg_remove_uisupporteddevices))) {
        strcat(args, "-u ");
    }
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(arg_remove_watch_app))) {
        strcat(args, "-w ");
    }
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(arg_enable_files_access))) {
        strcat(args, "-d ");
    }
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(arg_remove_app_extensions))) {
        strcat(args, "-e ");
    }
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(arg_remove_encrypted_extensions))) {
        strcat(args, "-g ");
    }
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(arg_substitute_instead_of_substrate))) {
        strcat(args, "-t ");
    }
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(arg_arm_bin4arm64))) {
        strcat(args, "-q ");
    }
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(fakesigns_ipa))) {
        strcat(args, "-s ");
    }
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(arg_bundle_id)) && gtk_entry_get_text(GTK_ENTRY(bundle_id_entry))[0] != '\0') {
        strcat(args, "-b ");
        strcat(args, gtk_entry_get_text(GTK_ENTRY(bundle_id_entry)));
        strcat(args, " ");
    }
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(arg_name)) && gtk_entry_get_text(GTK_ENTRY(name_entry))[0] != '\0') {
        strcat(args, "-n ");
        strcat(args, gtk_entry_get_text(GTK_ENTRY(name_entry)));
        strcat(args, " ");
    }
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(arg_version)) && gtk_entry_get_text(GTK_ENTRY(version_entry))[0] != '\0') {
        strcat(args, "-v ");
        strcat(args, gtk_entry_get_text(GTK_ENTRY(version_entry)));
        strcat(args, " ");
    }
    if (gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(arg_min_os)) && gtk_entry_get_text(GTK_ENTRY(min_os_entry))[0] != '\0') {
        strcat(args, "-m ");
        strcat(args, gtk_entry_get_text(GTK_ENTRY(min_os_entry)));
        strcat(args, " ");
    }

    if (file_path && output_path) {
        char command[2048];
        snprintf(command, sizeof(command), "pyzule -i %s -o %s -f %s %s", file_path, output_path, files_arg, args);
        system(command);
        g_free(file_path);
        g_free(output_path);
    } else {
        printf("Please select input and output files\n");
    }

    g_slist_free(file_list);
}

void open_file_dialog(GtkWidget *widget, gpointer data) {
    if (gtk_dialog_run(GTK_DIALOG(file_dialog)) == GTK_RESPONSE_ACCEPT) {
        char *file_path = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(file_dialog));
        gtk_label_set_text(GTK_LABEL(file_label), file_path);
        g_free(file_path);
    }
    gtk_widget_hide(file_dialog);
}

void open_output_dialog(GtkWidget *widget, gpointer data) {
    if (gtk_dialog_run(GTK_DIALOG(output_dialog)) == GTK_RESPONSE_ACCEPT) {
        char *output_path = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(output_dialog));
        gtk_label_set_text(GTK_LABEL(output_label), output_path);
        g_free(output_path);
    }
    gtk_widget_hide(output_dialog);
}

void open_files_dialog(GtkWidget *widget, gpointer data) {
    if (gtk_dialog_run(GTK_DIALOG(files_dialog)) == GTK_RESPONSE_ACCEPT) {
        GSList *file_list = gtk_file_chooser_get_filenames(GTK_FILE_CHOOSER(files_dialog));
        GSList *l;
        char files_text[1024] = "";
        for (l = file_list; l != NULL; l = l->next) {
            strcat(files_text, (char *) l->data);
            strcat(files_text, "\n");
            g_free(l->data);
        }
        gtk_label_set_text(GTK_LABEL(files_label), files_text);
        g_slist_free(file_list);
    }
    gtk_widget_hide(files_dialog);
}

void on_advance_button_clicked(GtkWidget *widget, gpointer data) {
    gboolean visible = gtk_widget_get_visible(advance_box);
    gtk_widget_set_visible(advance_box, !visible);
    gtk_button_set_label(GTK_BUTTON(widget), visible ? "Show Advanced" : "Hide Advanced");
}

void on_advance_check_button_toggled(GtkToggleButton *toggle_button, GtkWidget *entry) {
    gboolean active = gtk_toggle_button_get_active(toggle_button);
    gtk_widget_set_sensitive(entry, active);
}

int main(int argc, char *argv[]) {
    GtkWidget *window;
    GtkWidget *vbox;
    GtkWidget *file_button;
    GtkWidget *output_button;
    GtkWidget *files_button;
    GtkWidget *run_button;

    gtk_init(&argc, &argv);

    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "Pyzule-GUi");
    gtk_container_set_border_width(GTK_CONTAINER(window), 10);
    gtk_window_set_default_size(GTK_WINDOW(window), 400, 300);

    vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 6);
    gtk_container_add(GTK_CONTAINER(window), vbox);

    file_button = gtk_button_new_with_label("Select .ipa file");
    g_signal_connect(file_button, "clicked", G_CALLBACK(open_file_dialog), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), file_button, TRUE, TRUE, 0);

    file_label = gtk_label_new("No file selected");
    gtk_box_pack_start(GTK_BOX(vbox), file_label, TRUE, TRUE, 0);

    output_button = gtk_button_new_with_label("Select output file");
    g_signal_connect(output_button, "clicked", G_CALLBACK(open_output_dialog), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), output_button, TRUE, TRUE, 0);

    output_label = gtk_label_new("No file selected");
    gtk_box_pack_start(GTK_BOX(vbox), output_label, TRUE, TRUE, 0);

    files_button = gtk_button_new_with_label("Select files to inject");
    g_signal_connect(files_button, "clicked", G_CALLBACK(open_files_dialog), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), files_button, TRUE, TRUE, 0);

    files_label = gtk_label_new("No files selected");
    gtk_box_pack_start(GTK_BOX(vbox), files_label, TRUE, TRUE, 0);

    GtkWidget *hbox;

    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 6);
    arg_disable_compression = gtk_check_button_new_with_label("Disable Compression");
    gtk_box_pack_start(GTK_BOX(hbox), arg_disable_compression, FALSE, FALSE, 0);
 //   gtk_box_pack_start(GTK_BOX(hbox), gtk_label_new("Disable Compression"), FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, TRUE, TRUE, 0);

    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 6);
    arg_remove_uisupporteddevices = gtk_check_button_new_with_label("Remove Unsupported Devices");
    gtk_box_pack_start(GTK_BOX(hbox), arg_remove_uisupporteddevices, FALSE, FALSE, 0);
//    gtk_box_pack_start(GTK_BOX(hbox), gtk_label_new("Remove Unsupported Devices"), FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, TRUE, TRUE, 0);

    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 6);
    arg_remove_watch_app = gtk_check_button_new_with_label("Remove Watch App");
    gtk_box_pack_start(GTK_BOX(hbox), arg_remove_watch_app, FALSE, FALSE, 0);
//  gtk_box_pack_start(GTK_BOX(hbox), gtk_label_new("Remove Watch App"), FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, TRUE, TRUE, 0);

    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 6);
    arg_enable_files_access = gtk_check_button_new_with_label("Enable Files Access");
    gtk_box_pack_start(GTK_BOX(hbox), arg_enable_files_access, FALSE, FALSE, 0);
//    gtk_box_pack_start(GTK_BOX(hbox), gtk_label_new("Enable Files Access"), FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, TRUE, TRUE, 0);

    arg_remove_app_extensions = gtk_check_button_new_with_label("Remove App Extensions");
    gtk_box_pack_start(GTK_BOX(vbox), arg_remove_app_extensions, TRUE, TRUE, 0);

    arg_remove_encrypted_extensions = gtk_check_button_new_with_label("Remove Encrypted Extensions");
    gtk_box_pack_start(GTK_BOX(vbox), arg_remove_encrypted_extensions, TRUE, TRUE, 0);

    arg_substitute_instead_of_substrate = gtk_check_button_new_with_label("Use Substitute Instead Of Substrate");
    gtk_box_pack_start(GTK_BOX(vbox), arg_substitute_instead_of_substrate, TRUE, TRUE, 0);

    arg_arm_bin4arm64 = gtk_check_button_new_with_label("Thin All Binaries To arm64");
    gtk_box_pack_start(GTK_BOX(vbox), arg_arm_bin4arm64, TRUE, TRUE, 0);

    fakesigns_ipa = gtk_check_button_new_with_label("fakesigns The ipa (For Use With appsync)");
    gtk_box_pack_start(GTK_BOX(vbox), fakesigns_ipa, TRUE, TRUE, 0);

    advance_button = gtk_button_new_with_label("Show Advanced");
    g_signal_connect(advance_button, "clicked", G_CALLBACK(on_advance_button_clicked), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), advance_button, TRUE, TRUE, 0);

    advance_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 6);
    gtk_box_pack_start(GTK_BOX(vbox), advance_box, TRUE, TRUE, 0);

    GtkWidget *hbox_version = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 6);
    version_entry = gtk_entry_new();
    arg_version = gtk_check_button_new_with_label("Modify The App's Version");
    g_signal_connect(arg_version, "toggled", G_CALLBACK(on_advance_check_button_toggled), version_entry);
    gtk_box_pack_start(GTK_BOX(hbox_version), arg_version, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(hbox_version), version_entry, TRUE, TRUE, 0);
    gtk_widget_set_sensitive(version_entry, FALSE);
    gtk_box_pack_start(GTK_BOX(advance_box), hbox_version, TRUE, TRUE, 0);

    GtkWidget *hbox_name = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 6);
    name_entry = gtk_entry_new();
    arg_name = gtk_check_button_new_with_label("Modify The App's Name");
    g_signal_connect(arg_name, "toggled", G_CALLBACK(on_advance_check_button_toggled), name_entry);
    gtk_box_pack_start(GTK_BOX(hbox_name), arg_name, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(hbox_name), name_entry, TRUE, TRUE, 0);
    gtk_widget_set_sensitive(name_entry, FALSE);
    gtk_box_pack_start(GTK_BOX(advance_box), hbox_name, TRUE, TRUE, 0);

    GtkWidget *hbox_bundle_id = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 6);
    bundle_id_entry = gtk_entry_new();
    arg_bundle_id = gtk_check_button_new_with_label("Modify The App's Bundle Id");
    g_signal_connect(arg_bundle_id, "toggled", G_CALLBACK(on_advance_check_button_toggled), bundle_id_entry);
    gtk_box_pack_start(GTK_BOX(hbox_bundle_id), arg_bundle_id, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(hbox_bundle_id), bundle_id_entry, TRUE, TRUE, 0);
    gtk_widget_set_sensitive(bundle_id_entry, FALSE);
    gtk_box_pack_start(GTK_BOX(advance_box), hbox_bundle_id, TRUE, TRUE, 0);

    GtkWidget *hbox_min_os = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 6);
    min_os_entry = gtk_entry_new();
    arg_min_os = gtk_check_button_new_with_label("Change Minimum iOS Version");
    g_signal_connect(arg_min_os, "toggled", G_CALLBACK(on_advance_check_button_toggled), min_os_entry);
    gtk_box_pack_start(GTK_BOX(hbox_min_os), arg_min_os, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(hbox_min_os), min_os_entry, TRUE, TRUE, 0);
    gtk_widget_set_sensitive(min_os_entry, FALSE);
    gtk_box_pack_start(GTK_BOX(advance_box), hbox_min_os, TRUE, TRUE, 0);

    gtk_widget_set_visible(advance_box, FALSE);

    run_button = gtk_button_new_with_label("Run Pyzule");
    g_signal_connect(run_button, "clicked", G_CALLBACK(run_pyzule), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), run_button, TRUE, TRUE, 0);

    g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), NULL);

    file_dialog = gtk_file_chooser_dialog_new("Select IPA File",
                                              GTK_WINDOW(window),
                                              GTK_FILE_CHOOSER_ACTION_OPEN,
                                              "_Cancel", GTK_RESPONSE_CANCEL,
                                              "_Open", GTK_RESPONSE_ACCEPT,
                                              NULL);

    output_dialog = gtk_file_chooser_dialog_new("Select Output File",
                                                GTK_WINDOW(window),
                                                GTK_FILE_CHOOSER_ACTION_SAVE,
                                                "_Cancel", GTK_RESPONSE_CANCEL,
                                                "_Save", GTK_RESPONSE_ACCEPT,
                                                NULL);

    files_dialog = gtk_file_chooser_dialog_new("Select Files to Inject",
                                               GTK_WINDOW(window),
                                               GTK_FILE_CHOOSER_ACTION_OPEN,
                                               "_Cancel", GTK_RESPONSE_CANCEL,
                                               "_Open", GTK_RESPONSE_ACCEPT,
                                               NULL);

   gtk_file_chooser_set_select_multiple(GTK_FILE_CHOOSER(files_dialog), TRUE); //i really really fucking hate this shit took me like 2Hours for this dumb line

    gtk_widget_show_all(window);
    gtk_widget_set_visible(advance_box, FALSE); // Ensure advance_box is hidden initially
    gtk_main();

    return 0;
}
