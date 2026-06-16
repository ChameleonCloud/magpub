# Identifying Candidate Publications Using Google Scholar

Google Scholar — most permissive of all the sources. Indexes arXiv papers, GitHub-hosted papers, and — critically — PhD and master's theses. Almost no other aggregator indexes theses, which makes Google Scholar uniquely valuable; skip it and you miss a significant chunk of legitimate impact. The downside: it cannot be accessed programmatically. There is technically one paid unofficial API but even that isn't Google-endorsed, so practically speaking Google Scholar has to be worked manually. 

Our process uses Google Scholar's built-in library/saved lists feature to track what's been reviewed over time. For each Chameleon paper, pull the list of citing papers via the "Cited by" link, work through them, and save the ones worth importing to a dedicated list for that paper in your Google Scholar library.  To pull citing papers in Google Scholar: go to scholar.google.com, search for the paper, and click the "Cited by [N]" link below the result. This shows all papers Google Scholar has found that cite it. 

If there is no "Cited by" link, Google Scholar has no record of citations (does not mean it hasn't been cited elsewhere).

We maintain one saved list per Chameleon paper (for citation tracking) and a separate general list for keyword search matches ("Chameleon Cloud" OR "Chameleon Testbed"). The saved lists serve as the record of what's already been processed — anything already in a list has been reviewed.

To import a publication you want to add: copy the BibTeX citation from Google Scholar (click “Cite” and then “Bibtex” on the pop-up window) and use the BibTeX importer in the portal backend to upload it to the database.

We check citations for the following Chameleon publications:

- Lessons Learned from the Chameleon Testbed. Keahey K., Anderson J., Zhen Z., Riteau P., Ruth P., Stanzione D., Cevik M., Colleran J., Gunawi H.S., Hammock C., Mambretti J., Barnes A., Halbach F., Rocha A., Stubbs J. In Proceedings of the 2020 USENIX Annual Technical Conference (USENIX ATC '20), July 2020.
- CHI@Edge: Supporting Experimentation in the Edge to Cloud Continuum. Keahey K., Sherman M., Anderson J., Powers M. In Practice and Experience in Advanced Research Computing (PEARC '25), July 2025.
- CHI-in-a-Box: Reducing Operational Costs of Research Testbeds. Keahey K., Anderson J., Sherman M., et al. In Practice and Experience in Advanced Research Computing (PEARC '22), July 2022.
- Chameleon: A Large-Scale, Deeply Reconfigurable Testbed for Computer Science Research. Keahey K., Mambretti J., Ruth P., and Stanzione D. In Proceedings of MERIT 2019 at ICNP 2019, October 2019.
- Operational Lessons from Chameleon. Keahey K., Anderson J., Ruth P., et al. In Proceedings of HARC'19 at PEARC'19, July 2019.
- Chameleon: a Scalable Production Testbed for Computer Science Research. Keahey K., Riteau P., Stanzione D., et al. In Contemporary High Performance Computing, Volume 3. Chapman & Hall/CRC, May 2019.
- Keahey et al. (2021). Chameleon@Edge Community Workshop Report. https://doi.org/10.5281/zenodo.5777344
- Mambretti, Chen, and Yeh. "Next generation clouds, the chameleon cloud testbed, and software defined networking (sdn)." In ICCCRI 2015, IEEE.
