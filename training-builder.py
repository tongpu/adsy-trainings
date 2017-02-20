#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glob
import yaml
import jinja2
import subprocess

from pprint import pprint

BUILD_DIR   = "build"
COMMONS_DIR = "adsy-trainings-common.src"
TPL_PATH = "adsy-trainings-common.src/index/tpl.html"
IGNORE_TRAININGS = [
    "ansible-workshop",
    "suma-workshop"
]
INDEX_COPY_FILES=[
    "adcssy.min.css",
    "trainings.css"
]


def jinja2_basename_filter(path):
    return os.path.basename(path)


def render_template(tpl_path, context):
    path, filename = os.path.split(
        tpl_path
    )
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    )
    env.filters['basename'] = jinja2_basename_filter
    return env.get_template(filename).render(context)



def build_html(source_file, dest_file, commons_dir):
    pandoc_cmd_arr = [
        "pandoc",
        "--to",
        "revealjs",
        "--template",
        "{0}/revealjs-template.pandoc".format(
            commons_dir
        ),
        "--standalone",
        "--section-divs",
        "--no-highlight",
        source_file,
        "-o",
        dest_file
    ]
    subprocess.check_call(pandoc_cmd_arr)


def build_pdf(source_file, dest_file, commons_dir, build_path):

    otmp = "{0}/{1}.tmp.html".format(
        os.path.dirname( dest_file ),
        os.path.basename( dest_file )
    )

    # create a html that works with pdf css
    pandoc_cmd_arr = [
        "pandoc",
        "-c",
        "../../commons/topdf/style.css",
        source_file,
        "-o",
        otmp
    ]
    subprocess.check_call(pandoc_cmd_arr)

    # then convert this to html
    wkhtmltopdf_cmd_arr = [
        "wkhtmltopdf",
        "--page-width",
        "200",
        "--page-height",
        "145",
        otmp,
        dest_file
    ]
    subprocess.check_call(wkhtmltopdf_cmd_arr)

    # delete temp file
    os.remove(otmp)



    #sys.exit(0)
    # #return
    # tmp_build_path = "{0}/tmp/tmp-slide-".format(
    #     build_path
    # )
    # # Build single pdf files
    # phantomjs_cmd_arr = [
    #     "phantomjs",
    #     "{0}/phantomjs-revealjs-capture.js".format(
    #         commons_dir
    #     ),
    #     source_file,
    #     tmp_build_path
    # ]
    # print(source_file)
    # print(" ".join(phantomjs_cmd_arr))
    #
    # subprocess.check_call(phantomjs_cmd_arr)
    #
    # # combine single pdf's to a single one
    # tmp_slides = glob.glob(
    #     "{0}*.pdf".format(
    #         tmp_build_path
    #     )
    # )
    # tmp_slides = sorted(tmp_slides)
    # gscmd_array = [
    #     "gs",
    #     "-q",
    #     "-dPDFSETTINGS=/printer",
    #     "-dNOPAUSE",
    #     "-dBATCH",
    #     "-sDEVICE=pdfwrite",
    #     "-sOutputFile={0}".format(
    #         dest_file
    #     )
    # ]
    # gscmd_array += tmp_slides
    # subprocess.check_call(gscmd_array)
    # #print(" ".join(gscmd_array))
    #
    # for tmp_slide in tmp_slides:
    #     os.remove(tmp_slide)

    #sys.exit(0)




def main():

    root_dir = os.path.dirname(
        os.path.realpath( __file__ )
    )

    commons_dir_abs = "{0}/{1}".format(
        root_dir,
        COMMONS_DIR
    )

    index_files = glob.glob(
        "**/*yml",
        recursive = True
    )

    training_list = {}

    ## Copy commons files first for phantom
    subprocess.check_call([
        "cp",
        "-ra",
        commons_dir_abs,
        "{0}/{1}/commons".format(
            root_dir,
            BUILD_DIR,
        )
    ])


    for yaml_file in sorted(index_files):

        training_dir = os.path.dirname( yaml_file )
        rdir = training_dir.split("/")[0]
        if rdir in IGNORE_TRAININGS:
            continue

        source_dir = "{0}/{1}".format(
            root_dir,
            training_dir
        )
        build_path = "{0}/{1}/{2}".format(
            root_dir,
            BUILD_DIR,
            training_dir
        )
        build_path_root_abs = "{0}/{1}".format(
            root_dir,
            BUILD_DIR
        )

        yf = open(yaml_file)
        training_yaml = yaml.load(yf)
        tt = {
            "category": training_yaml['Area'],
            "name": training_yaml['Name'],
            "description": training_yaml['Description'],
            "files_html": [],
            "files_pdf": []
        }
        if training_yaml['Area'] not in training_list:
            training_list[training_yaml['Area']] = []

        print("Building: {0}".format(training_dir))

        # Find all Markdown files in currend dir
        os.makedirs( build_path, exist_ok=True )
        markdown_files = glob.glob(
            "{0}/*md".format(source_dir)
        )

        # Build HTML files from Markdown
        for md in markdown_files:
            fname_no_ext = os.path.splitext(
                os.path.basename( md )
            )[0]
            html_build_file = "{0}/{1}.html".format(
                build_path,
                fname_no_ext
            )
            pdf_build_file = "{0}/{1}.pdf".format(
                build_path,
                fname_no_ext
            )

            tt['files_html'].append(
                "{0}/{1}.html".format(
                    training_dir,
                    fname_no_ext
                )
            )
            print("   > {0}.html".format(fname_no_ext))
            build_html(md, html_build_file, commons_dir_abs)


        # copy image dirs
        static_dirs = [ name for name in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, name)) ]
        for sdir in static_dirs:
            src = "{0}/{1}/{2}".format(
                root_dir,
                training_dir,
                sdir
            )
            dst = "{0}/{1}/{2}/{3}".format(
                root_dir,
                BUILD_DIR,
                training_dir,
                sdir
            )
            subprocess.check_call([
                "cp",
                "-ra",
                src,
                dst
            ])

        # then build pdf from generated html
        for htmlf in tt['files_html']:
            fname_no_ext = os.path.splitext(
                os.path.basename( htmlf )
            )[0]
            html_build_file = "{0}/{1}.html".format(
                build_path,
                fname_no_ext
            )
            pdf_output = "{0}/{1}.pdf".format(
                build_path,
                fname_no_ext
            )
            print("   > {0}.pdf".format(fname_no_ext))

            build_pdf(
                html_build_file,
                pdf_output,
                commons_dir_abs,
                build_path_root_abs
            )

            tt['files_pdf'].append(
                "{0}/{1}.pdf".format(
                    training_dir,
                    fname_no_ext
                )
            )

        # append to dict for index file
        tt['files_html'] = sorted(tt['files_html'])
        tt['files_pdf']  = sorted(tt['files_pdf'])
        training_list[training_yaml['Area']].append(tt)


    ## Build the index template
    context = {
         "training_list": training_list
    }
    output_index_html = render_template(TPL_PATH, context)
    output_index = "{0}/{1}/index.html".format(
        root_dir,
        BUILD_DIR
    )
    file_object  = open(output_index, "w")
    file_object.write(
        output_index_html
    )


    # copy css for index
    for css in INDEX_COPY_FILES:
        src = "{0}/index/{1}".format(
            commons_dir_abs,
            css
        )
        dst = "{0}/{1}/{2}".format(
            root_dir,
            BUILD_DIR,
            css
        )
        subprocess.check_call([
            "cp",
            src,
            dst
        ])






if __name__ == '__main__':
    main()
