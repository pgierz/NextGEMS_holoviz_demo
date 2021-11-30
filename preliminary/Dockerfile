FROM jupyter/scipy-notebook:lab-3.2.3

COPY data ${HOME}/data
COPY README.md Holoviz_Icon_Example.ipynb ${HOME}
COPY environment.yml ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

RUN mamba install python=3.9.7 --yes --quiet
RUN mamba install -c pyviz holoviz --yes --quiet
RUN mamba install -c pyviz geoviews --yes --quiet 
RUN mamba install -c conda-forge cartopy --yes --quiet 
